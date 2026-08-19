$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python (Join-Path $ScriptDir 'shadowctl.py') uninstall @args
