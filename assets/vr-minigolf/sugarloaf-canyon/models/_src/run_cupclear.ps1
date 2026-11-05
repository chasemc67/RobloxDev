param([string]$Py='cup_clear.py',[string]$Tag='before')
$m='C:\Users\chase\sc\sugarloaf-canyon\models'
$p=Start-Process -FilePath 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -ArgumentList @('-b','--factory-startup','-P',"$m\_src\$Py",'--',$m,"$m\_src\cupclear_$Tag.json") -WindowStyle Hidden -PassThru -Wait -RedirectStandardOutput "$m\_src\cupclear_$Tag.log" -RedirectStandardError "$m\_src\cupclear_$Tag.log.stderr"
"exit $($p.ExitCode)" | Add-Content "$m\_src\cupclear_$Tag.log"
