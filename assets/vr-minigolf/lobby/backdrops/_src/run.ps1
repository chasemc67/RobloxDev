$w='C:\Users\chase\bw_backdrops'
Remove-Item "$w\DONE.txt" -EA SilentlyContinue
$p=Start-Process -FilePath 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -ArgumentList @('-b','--factory-startup','-P',"`"$w\_src\build_backdrops.py`"",'--',"`"$w`"",'--render','--cpu','--only','SL1') -WindowStyle Hidden -PassThru -Wait -RedirectStandardOutput "$w\_src\build.log" -RedirectStandardError "$w\_src\build.log.stderr"
Set-Content "$w\DONE.txt" "exit $($p.ExitCode)"
