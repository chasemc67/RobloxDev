$ErrorActionPreference='Stop'
$props=@('h06_sluice_gate','h06_sluice_frame','h11_lock_gate','h11_lock_lift','h11_lock_chamber','h11_quay_lip')
$outputDir=Join-Path (Split-Path $PSScriptRoot -Parent) 'previews\cycles\final'
foreach ($prop in $props) {
 & (Join-Path $PSScriptRoot 'blender_pass3.ps1') -Script render_pc.py -Log ('cycles_pass3_'+$prop+'.log') -ExtraArgs @('--','--input',(Join-Path $PSScriptRoot ($prop+'.blend')),'--id',$prop,'--output',$outputDir)
 foreach ($view in @('rest_eye','rest_34','max_eye','max_34')) {
  if (-not (Test-Path -LiteralPath (Join-Path $outputDir ($prop+'_'+$view+'.png')))) { throw "Missing final preview: $prop $view" }
 }
}
while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 30 }
Add-Content (Join-Path $PSScriptRoot 'PROGRESS.md') "`n- $((Get-Date).ToString('o')) FINAL Cycles OptiX render batch complete; no Blender running."
