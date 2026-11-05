$d='C:\Users\chase\3dmb_sugar_tankdock'
while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 30 }
$p=Start-Process -FilePath 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -ArgumentList @('-b','--factory-startup','-P',"`"$d\build_tankdock.py`"",'--',"`"$d`"") -WindowStyle Hidden -PassThru -Wait -RedirectStandardOutput "$d\build.log" -RedirectStandardError "$d\build.log.stderr"
Set-Content "$d\done.flag" "exit $($p.ExitCode)"
