$ErrorActionPreference = "Stop"

$workspace = $PSScriptRoot
while ($workspace -and (Test-Path $workspace)) {
  if (Test-Path (Join-Path $workspace "jpf-core-symbc")) {
    break
  }
  $parent = Split-Path -Parent $workspace
  if ($parent -eq $workspace -or -not $parent) {
    $workspace = $PSScriptRoot
    break
  }
  $workspace = $parent
}
Push-Location $workspace

$javaHome = $null
$javaCandidates = @(
  "C:\Program Files\RedHat\java-1.8.0-openjdk-1.8.0.422-1",
  (Join-Path $workspace "tools\jdk8\jdk8u482-b08")
)
if ($env:JAVA_HOME) {
  $javaCandidates = $javaCandidates + $env:JAVA_HOME
}
$oldErrorAction = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
foreach ($candidate in $javaCandidates) {
  if ($candidate -and (Test-Path (Join-Path $candidate "bin\java.exe"))) {
    $versionInfo = & (Join-Path $candidate "bin\java.exe") -version 2>&1 | Out-String
    if ($versionInfo -like "*1.8.0*" -or $versionInfo -like "* 1.8.*") {
      $javaHome = $candidate
      break
    }
  }
}
$ErrorActionPreference = $oldErrorAction

if (-not $javaHome) {
  foreach ($candidate in $javaCandidates) {
    if ($candidate -and (Test-Path (Join-Path $candidate "bin\java.exe"))) {
      $javaHome = $candidate
      break
    }
  }
}
if (-not $javaHome) {
  throw "No working Java 8 installation found. Please set JAVA_HOME."
}
$jpfCore = Join-Path $workspace "jpf-core-symbc"
$jpfSymbc = Join-Path $workspace "jpf-symbc"
$resultsDir = Join-Path $workspace "results-oop"
$runJpfJar = Join-Path $jpfCore "build\RunJPF.jar"
$z3Jar = Join-Path $jpfSymbc "lib\com.microsoft.z3.jar"
$analysisScript = Join-Path $workspace "analyze-oop-study.py"

$benchmarks = @(
  "oop-baselineKernel",
  "oop-loopControlKernel",
  "oop-guardedExceptionControl",
  "oop-exceptionTryCatch",
  "oop-directDispatchControl",
  "oop-polymorphicDispatch"
)

$warmupRuns = 5
$repetitions = 20
$perRunTimeoutSec = 20
$searchClass = ""
$searchLabel = ""
if ($args.Length -ge 1) {
  $repetitions = [int]$args[0]
}
if ($args.Length -ge 2) {
  $benchmarks = $args[1].Split(",")
}
if ($args.Length -ge 3) {
  $warmupRuns = [int]$args[2]
}
if ($args.Length -ge 4) {
  $perRunTimeoutSec = [int]$args[3]
}
if ($args.Length -ge 5) {
  $searchClass = $args[4]
  if ($searchClass -eq "none" -or $searchClass -eq "default") {
    $searchClass = ""
  }
}
if ($args.Length -ge 6) {
  $resultsDir = Join-Path $workspace $args[5]
}
if ($args.Length -ge 7) {
  $searchLabel = $args[6]
}

if (-not $searchLabel -and $searchClass) {
  $searchLabel = [System.IO.Path]::GetFileName($searchClass)
}
if (-not $searchLabel) {
  $searchLabel = "default"
}

New-Item -ItemType Directory -Force -Path $resultsDir | Out-Null
Get-ChildItem $resultsDir -Filter *.csv -ErrorAction SilentlyContinue | Remove-Item -Force
$timeoutLog = Join-Path $resultsDir "timeouts.log"
if (Test-Path $timeoutLog) {
  Remove-Item -LiteralPath $timeoutLog -Force
}
$failureLog = Join-Path $resultsDir "failures.log"
if (Test-Path $failureLog) {
  Remove-Item -LiteralPath $failureLog -Force
}

$env:JAVA_HOME = $javaHome
$env:PATH = "$javaHome\bin;$jpfSymbc\lib;$jpfSymbc\lib\64bit;" + $env:PATH

Write-Host "Using JAVA_HOME=$javaHome"
Write-Host "Results directory: $resultsDir"
Write-Host "Warmup runs per benchmark: $warmupRuns"
Write-Host "Measured runs per benchmark: $repetitions"
Write-Host "Per-run timeout (sec): $perRunTimeoutSec"
Write-Host "Search class override: $searchClass"
Write-Host "Search label: $searchLabel"
Write-Host "Benchmarks: $($benchmarks -join ', ')"

foreach ($benchmark in $benchmarks) {
  $csvPath = Join-Path $resultsDir "$benchmark.csv"
  $summaryCsvPath = Join-Path $resultsDir "$benchmark`_summary.csv"
  $jpfFile = Join-Path $jpfSymbc "src\examples\research\$benchmark.jpf"

  Write-Host ""
  Write-Host "=== Warmup $benchmark ==="
  for ($i = 1; $i -le $warmupRuns; $i++) {
    Write-Host "[$benchmark] warmup $i / $warmupRuns"
    $argString = ('-cp "{0};{1}" gov.nasa.jpf.tool.RunJPF "+research.output={2}" "+research.append=true" "+research.run_id={3}" "{4}"' -f
      $runJpfJar,
      $z3Jar,
      (Join-Path $resultsDir "_warmup.csv"),
      "$benchmark-warmup-$i",
      $jpfFile)
    if ($searchClass) {
      $argString += (' "+search.class={0}"' -f $searchClass)
    }
    $argString += (' "+research.search_label={0}" "+research.benchmark={1}"' -f $searchLabel, $benchmark)
    $proc = Start-Process -FilePath "$javaHome\bin\java.exe" -ArgumentList $argString -PassThru -WindowStyle Hidden
    $timedOut = $false
    try {
      Wait-Process -Id $proc.Id -Timeout $perRunTimeoutSec -ErrorAction Stop
    } catch {
      $timedOut = $true
    }
    if ($timedOut) {
      Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
      Add-Content -Path $timeoutLog -Value "$benchmark,warmup,$i,$perRunTimeoutSec"
      Write-Host "[$benchmark] warmup timed out and was stopped"
      continue
    }
    $proc.Refresh()
    if ($proc.ExitCode -ne 0) {
      Add-Content -Path $failureLog -Value "$benchmark,warmup,$i,$($proc.ExitCode)"
      Write-Host "[$benchmark] warmup failed with exit code $($proc.ExitCode)"
    }
  }

  if (Test-Path $csvPath) {
    Remove-Item -LiteralPath $csvPath -Force
  }
  if (Test-Path $summaryCsvPath) {
    Remove-Item -LiteralPath $summaryCsvPath -Force
  }

  Write-Host "=== Measure $benchmark ==="
  for ($i = 1; $i -le $repetitions; $i++) {
    Write-Host "[$benchmark] measured $i / $repetitions"
    $argString = ('-cp "{0};{1}" gov.nasa.jpf.tool.RunJPF "+research.output={2}" "+research.append=true" "+research.run_id={3}" "{4}"' -f
      $runJpfJar,
      $z3Jar,
      $csvPath,
      "$benchmark-run-$i",
      $jpfFile)
    if ($searchClass) {
      $argString += (' "+search.class={0}"' -f $searchClass)
    }
    $argString += (' "+research.search_label={0}" "+research.benchmark={1}"' -f $searchLabel, $benchmark)
    $proc = Start-Process -FilePath "$javaHome\bin\java.exe" -ArgumentList $argString -PassThru -WindowStyle Hidden
    $timedOut = $false
    try {
      Wait-Process -Id $proc.Id -Timeout $perRunTimeoutSec -ErrorAction Stop
    } catch {
      $timedOut = $true
    }
    if ($timedOut) {
      Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
      Add-Content -Path $timeoutLog -Value "$benchmark,measured,$i,$perRunTimeoutSec"
      Write-Host "[$benchmark] measured run timed out and was stopped"
      continue
    }
    $proc.Refresh()
    if ($proc.ExitCode -ne 0) {
      Add-Content -Path $failureLog -Value "$benchmark,measured,$i,$($proc.ExitCode)"
      Write-Host "[$benchmark] measured run failed with exit code $($proc.ExitCode)"
    }
  }

  if (Test-Path $csvPath) {
    $rows = (Get-Content $csvPath | Measure-Object -Line).Lines - 1
    Write-Host "[$benchmark] rows written: $rows"
  }
}

if (Test-Path (Join-Path $resultsDir "_warmup.csv")) {
  Remove-Item -LiteralPath (Join-Path $resultsDir "_warmup.csv") -Force
}

python $analysisScript $resultsDir
Pop-Location
