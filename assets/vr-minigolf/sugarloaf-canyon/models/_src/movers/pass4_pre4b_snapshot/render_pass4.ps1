$ErrorActionPreference='Stop'
$props=@('h09_windpump_vanes','h09_windpump_hub','h14_ore_bucket','h14_cableway_trestle','h17_shadow_arms','h17_plinth','h07_bridge_parapets','h07_bridge_skirts','h07_gap_floor_mist','h07_teleport_pads','h07_teleport_pad_exit','dam_crest_parapets')
$outputDir=Join-Path (Split-Path $PSScriptRoot -Parent) 'previews\cycles\pass4'
foreach ($prop in $props) {
 & (Join-Path $PSScriptRoot 'blender_pass4.ps1') -Script render_pc.py -Log ('cycles_pass4_'+$prop+'.log') -ExtraArgs @('--','--input',(Join-Path $PSScriptRoot ($prop+'.blend')),'--id',$prop,'--output',$outputDir)
}
foreach ($hole in @('h07','h09','h14','h17')) {
 & (Join-Path $PSScriptRoot 'blender_pass4.ps1') -Script render_pc.py -Log ('cycles_pass4_tee_'+$hole+'.log') -ExtraArgs @('--','--hole',$hole,'--output',$outputDir)
 if (-not (Test-Path -LiteralPath (Join-Path $outputDir ($hole+'_tee_eye.png')))) { throw "Missing tee view: $hole" }
}
while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 30 }
Add-Content (Join-Path $PSScriptRoot 'PROGRESS.md') "`n- $((Get-Date).ToString('o')) FINAL pass-4 Cycles OptiX render batch complete; no Blender running."
