# Registers the okpdf: link type for this Windows user (HKCU, no admin). Undo: Remove-Item HKCU:\Software\Classes\okpdf -Recurse
$h = Join-Path $PSScriptRoot 'okpdf.js'
$k = 'HKCU:\Software\Classes\okpdf'
New-Item -Path "$k\shell\open\command" -Force | Out-Null
Set-ItemProperty -Path $k -Name '(default)' -Value 'URL:Open PDF in Okular'
Set-ItemProperty -Path $k -Name 'URL Protocol' -Value ''
Set-ItemProperty -Path "$k\shell\open\command" -Name '(default)' -Value "wscript.exe //nologo //B `"$h`" `"%1`""
Get-ItemProperty "$k\shell\open\command"
