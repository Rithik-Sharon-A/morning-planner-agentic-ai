# Run backend with venv Python (no activation needed)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
& "$ScriptDir\venv\Scripts\python.exe" "$ScriptDir\main.py"
