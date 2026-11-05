$ErrorActionPreference='Continue'
$bl='C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$log='C:\Users\chase\ghosts\run.log'
"$(Get-Date) start" | Out-File $log
while (Get-Process blender -EA SilentlyContinue) { "$(Get-Date) waiting for blender" | Add-Content $log; Start-Sleep 30 }
& $bl -b --factory-startup -P C:\Users\chase\ghosts\_src\build_ghosts.py -- C:\Users\chase\ghosts *>> $log
Set-Location C:\Users\chase\bw\boardwalk\models\_src
& $bl -b --factory-startup -P build_all.py -- --only bw_string_lights *>> $log
& $bl -b --factory-startup -P render_props.py -- --only bw_string_lights *>> $log
"ALLDONE $(Get-Date)" | Add-Content $log
