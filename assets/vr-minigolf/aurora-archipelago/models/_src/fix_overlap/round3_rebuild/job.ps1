param([string]$Py,[string]$Tag)
$W='C:\Users\chase\aa_fix3'
$bl='C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$args2=@('-b','--factory-startup','--python-exit-code','1','-P',"$W\$Py",'--')+((Get-Content "C:\Users\chase\aa_fix3\$Tag.args" -Raw).Trim() -split '\|')
$p=Start-Process -FilePath $bl -ArgumentList $args2 -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput "$W\$Tag.out.log" -RedirectStandardError "$W\$Tag.err.log"
Set-Content "$W\$Tag.done" "exit $($p.ExitCode)"
