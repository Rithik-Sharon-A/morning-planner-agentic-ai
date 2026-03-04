# Safe removal of unused agent files (legacy schedule/preference/logistics).
# Run only after reading docs/CLEANUP_AND_REFACTOR_REPORT.md and confirming
# that crewai_agents.py does not import these modules.
# Execute from repository root or backend directory.

$ErrorActionPreference = "Stop"
# If this script lives in backend/scripts/, backend is parent of PSScriptRoot
$BackendDir = (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path (Join-Path $BackendDir "agents"))) {
    $BackendDir = $PSScriptRoot
}
$AgentsDir = Join-Path $BackendDir "agents"

$ToRemove = @(
    "schedule.py",
    "preference.py",
    "logistics.py"
)

foreach ($f in $ToRemove) {
    $path = Join-Path $AgentsDir $f
    if (Test-Path $path) {
        Remove-Item -Path $path -Force
        Write-Host "Removed: $path"
    } else {
        Write-Host "Not found (skip): $path"
    }
}

Write-Host "Done. Run tests or smoke-check the app to confirm nothing broke."
