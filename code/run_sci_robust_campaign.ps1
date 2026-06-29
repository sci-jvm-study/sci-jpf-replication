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
$resultsDir = Join-Path $workspace "paper_1\Artifacts\results\results-robust-campaign"
$runJpfJar = Join-Path $jpfCore "build\RunJPF.jar"
$z3Jar = Join-Path $jpfSymbc "lib\com.microsoft.z3.jar"

# The target benchmarks representing diverse JVM-overhead characteristics
$benchmarks = @(
  @{ label = "mixed-dispatch-branches"; jpf = "src\examples\research\mixed-dispatch-branches.jpf" },
  @{ label = "real-factories-depth6-realstyle"; jpf = "src\examples\research\real-factories-depth6-realstyle.jpf" },
  @{ label = "adverse-dispatch-branches"; jpf = "src\examples\research\adverse-dispatch-branches.jpf" },
  @{ label = "real-treemap"; jpf = "src\examples\research\real-treemap.jpf" },
  @{ label = "real-decisiongraph"; jpf = "src\examples\research\real-decisiongraph.jpf" }
)

# Comparative scheduling strategies
$strategies = @(
  @{ class = "gov.nasa.jpf.search.heuristic.BFSHeuristic"; label = "BFS" },
  @{ class = "gov.nasa.jpf.search.heuristic.DFSHeuristic"; label = "DFS" },
  @{ class = "gov.nasa.jpf.search.heuristic.RandomHeuristic"; label = "Random" },
  @{ class = "gov.nasa.jpf.search.heuristic.SCISearch"; label = "SCI" }
)

# Strict budget increments
$stateBudgets = @(5, 10, 20, 50, 100, 200, 500)

$repetitions = 3
$warmupRuns = 1
$perRunTimeoutSec = 15

# Create clean results directory
if (Test-Path $resultsDir) {
  Remove-Item -Path $resultsDir -Recurse -Force | Out-Null
}
New-Item -ItemType Directory -Force -Path $resultsDir | Out-Null

$env:JAVA_HOME = $javaHome
$env:PATH = "$javaHome\bin;$jpfSymbc\lib;$jpfSymbc\lib\64bit;" + $env:PATH

Write-Host "======================================================"
Write-Host "  SCI-Guided Robust Campaign Execution (Re-run)      "
Write-Host "======================================================"
Write-Host "State Budgets: $($stateBudgets -join ', ')"
Write-Host "Strategies: BFS, DFS, Random, SCI"
Write-Host "Repetitions: $repetitions"
Write-Host "Results folder: $resultsDir"
Write-Host "------------------------------------------------------"

foreach ($bench in $benchmarks) {
  $benchLabel = $bench.label
  $jpfFile = Join-Path $jpfSymbc $bench.jpf
  
  Write-Host ""
  Write-Host ">>>>>>>> Benchmark: $benchLabel <<<<<<<<"
  
  foreach ($strategy in $strategies) {
    $class = $strategy.class
    $label = $strategy.label
    
    Write-Host "  >>> Strategy: $label ($class) <<<"
    
    foreach ($budget in $stateBudgets) {
      $runLabel = "$benchLabel`_$label`_limit_$budget"
      $csvPath = Join-Path $resultsDir "$runLabel.csv"
      
      Write-Host "    Running limit=$budget..."
      
      # 1. Warmup
      for ($i = 1; $i -le $warmupRuns; $i++) {
        $argString = ('-cp "{0};{1}" gov.nasa.jpf.tool.RunJPF "+research.output={2}" "+research.append=true" "+research.run_id={3}" "+search.class={4}" "+research.search_label={5}" "+research.benchmark={6}" "+listener=gov.nasa.jpf.listener.BudgetChecker,gov.nasa.jpf.symbc.ResearchDataListener" "+budget.max_state={7}" "{8}"' -f
          $runJpfJar,
          $z3Jar,
          (Join-Path $resultsDir "_warmup.csv"),
          "$runLabel-warmup-$i",
          $class,
          $label,
          $benchLabel,
          $budget,
          $jpfFile)
        
        $proc = Start-Process -FilePath "$javaHome\bin\java.exe" -ArgumentList $argString -PassThru -WindowStyle Hidden
        $timedOut = $false
        try {
          Wait-Process -Id $proc.Id -Timeout $perRunTimeoutSec -ErrorAction Stop
        } catch {
          $timedOut = $true
        }
        if ($timedOut) {
          Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        }
      }
      
      # 2. Measurement Runs
      for ($i = 1; $i -le $repetitions; $i++) {
        $argString = ('-cp "{0};{1}" gov.nasa.jpf.tool.RunJPF "+research.output={2}" "+research.append=true" "+research.run_id={3}" "+search.class={4}" "+research.search_label={5}" "+research.benchmark={6}" "+listener=gov.nasa.jpf.listener.BudgetChecker,gov.nasa.jpf.symbc.ResearchDataListener" "+budget.max_state={7}" "{8}"' -f
          $runJpfJar,
          $z3Jar,
          $csvPath,
          "$runLabel-run-$i",
          $class,
          $label,
          $benchLabel,
          $budget,
          $jpfFile)
        
        $proc = Start-Process -FilePath "$javaHome\bin\java.exe" -ArgumentList $argString -PassThru -WindowStyle Hidden
        $timedOut = $false
        try {
          Wait-Process -Id $proc.Id -Timeout $perRunTimeoutSec -ErrorAction Stop
        } catch {
          $timedOut = $true
        }
        if ($timedOut) {
          Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
          Write-Host "      [$runLabel] Run $i timed out!"
        }
      }
    }
  }
}

  Remove-Item -LiteralPath (Join-Path $resultsDir "_warmup.csv") -Force
}
  Remove-Item -LiteralPath (Join-Path $resultsDir "_warmup_summary.csv") -Force
}

Write-Host ""
Write-Host "SCI Robust Campaign completed successfully. Raw results saved to $resultsDir"
Pop-Location
