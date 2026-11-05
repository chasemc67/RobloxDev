param([switch]$Review)
$ErrorActionPreference = 'Continue'
$blenderExe = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$srcDir = $PSScriptRoot
$outputDir = Join-Path (Split-Path $srcDir -Parent) 'previews\cycles'
if ($Review) { $outputDir = Join-Path $outputDir 'review' }
$props = @('h06_sluice_gate','h06_sluice_frame','h11_lock_gate','h11_lock_lift','h11_lock_chamber')
foreach ($prop in $props) {
    while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 5 }
    Add-Content (Join-Path $srcDir 'PROGRESS.md') "`n- $((Get-Date).ToString('o')) Starting Cycles OptiX final views: $prop; process check clear."
    $extraArgs = @()
    if ($Review) { $extraArgs = @('--allow-draft') }
    & $blenderExe -b -P (Join-Path $srcDir 'render_pc.py') -- --input (Join-Path $srcDir ($prop+'.blend')) --id $prop --output $outputDir @extraArgs *> (Join-Path $srcDir ('cycles_'+$prop+'.log'))
    $requiredViews = @('rest_eye','rest_34','max_eye','max_34')
    foreach ($view in $requiredViews) {
        if (-not (Test-Path -LiteralPath (Join-Path $outputDir ($prop+'_'+$view+'.png')))) { throw "Missing final preview: $prop $view; inspect Cycles log." }
    }
}
while (Get-Process blender -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 5 }
Add-Content (Join-Path $srcDir 'PROGRESS.md') "`n- $((Get-Date).ToString('o')) Final render batch complete, no Blender process running."
