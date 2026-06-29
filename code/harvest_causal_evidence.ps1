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
$runJpfJar = Join-Path $jpfCore "build\RunJPF.jar"
$z3Jar = Join-Path $jpfSymbc "lib\com.microsoft.z3.jar"

$env:JAVA_HOME = $javaHome
$env:PATH = "$javaHome\bin;$jpfSymbc\lib;$jpfSymbc\lib\64bit;" + $env:PATH

$configs = @(
  @{ name = "Polymorphic Dynamic Dispatch"; file = "real-factories-depth6-realstyle.jpf" },
  @{ name = "Direct Branch Control"; file = "real-factories-depth6-branchcontrol.jpf" }
)

Write-Host "======================================================"
Write-Host "  Harvesting Direct VM Causal Profiling Metrics       "
Write-Host "======================================================"

$results = @()

foreach ($config in $configs) {
  $name = $config.name
  $file = Join-Path $jpfSymbc "src\examples\research\$($config.file)"
  
  Write-Host "Running JPF on $name..."
  
  # Run JPF inline and capture output synchronously
  $logContent = & "$javaHome\bin\java.exe" -cp "$runJpfJar;$z3Jar" gov.nasa.jpf.tool.RunJPF "$file" 2>&1 | Out-String
  
  # Parse stats
  $newStates = 0
  $backtracked = 0
  $cgs = 0
  $heapNew = 0
  $gcCycles = 0
  $instructions = 0
  
  # Extract states: new=1457,visited=0,backtracked=1457,end=729
  if ($logContent -match 'states:\s+new=(\d+),visited=\d+,backtracked=(\d+)') {
    $newStates = $Matches[1]
    $backtracked = $Matches[2]
  }
  # Extract choice generators:  thread=1 (signal=0,lock=1,sharedRef=0,threadApi=0,reschedule=0), data=728
  if ($logContent -match 'choice generators:\s+.*data=(\d+)') {
    $cgs = $Matches[1]
  }
  # Extract heap:               new=20441,released=27359,maxLive=372,gcCycles=1093
  if ($logContent -match 'heap:\s+new=(\d+),.*gcCycles=(\d+)') {
    $heapNew = $Matches[1]
    $gcCycles = $Matches[2]
  }
  # Extract instructions:       639037
  if ($logContent -match 'instructions:\s+(\d+)') {
    $instructions = $Matches[1]
  }
  
  $results += [PSCustomObject]@{
    "Configuration"   = $name
    "States Stored"   = $newStates
    "Backtracks"      = $backtracked
    "ChoiceGens"      = $cgs
    "Heap Allocated"  = $heapNew
    "GC Cycles"       = $gcCycles
    "Bytecodes Run"   = $instructions
  }
}

Write-Host ""
Write-Host "======================================================================================="
Write-Host "               DIRECT VM-LEVEL CAUSAL ENGINE ATTRIBUTION PROFILE                       "
Write-Host "======================================================================================="
$results | Format-Table -AutoSize
Write-Host "======================================================================================="

# Also write to CSV for easy record-keeping
$results | Export-Csv -Path (Join-Path $PSScriptRoot "..\results\results-sci-budget\causal_profiling.csv") -NoTypeInformation
Write-Host "Causal profiling data exported to results-sci-budget\causal_profiling.csv"
Pop-Location
