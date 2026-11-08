@echo off
rem Sequential pipeline, one Blender process at a time. Paths relative to this script.
rem Usage: run_all.cmd [BLENDER_EXE] [CONCEPT_IMAGE]
rem Writes ..\pro_shop_pavilion_v1.blend, textures\, manifest/validation/report, previews\, derived\ (FBX).
setlocal
set "SRC=%~dp0"
set "OUT=%SRC%.."
set "BLENDER=%~1"
if "%BLENDER%"=="" set "BLENDER=C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
set "CONCEPT=%~2"
if not exist "%OUT%\logs" mkdir "%OUT%\logs"
echo START %DATE% %TIME% > "%OUT%\logs\pipeline.log"
"%BLENDER%" --background --factory-startup --python "%SRC%generate_pavilion.py" -- --output "%OUT%\pro_shop_pavilion_v1.blend" --texdir "%OUT%\textures" > "%OUT%\logs\generate.log" 2>&1
echo generate exit %ERRORLEVEL% >> "%OUT%\logs\pipeline.log"
"%BLENDER%" --background "%OUT%\pro_shop_pavilion_v1.blend" --python "%SRC%validate_pavilion.py" -- --outdir "%OUT%" > "%OUT%\logs\validate.log" 2>&1
echo validate exit %ERRORLEVEL% >> "%OUT%\logs\pipeline.log"
"%BLENDER%" --background "%OUT%\pro_shop_pavilion_v1.blend" --python "%SRC%render_pavilion.py" -- --outdir "%OUT%\previews" --device CPU --samples 64 > "%OUT%\logs\render.log" 2>&1
echo render exit %ERRORLEVEL% >> "%OUT%\logs\pipeline.log"
"%BLENDER%" --background "%OUT%\pro_shop_pavilion_v1.blend" --python "%SRC%export_fbx.py" -- --output "%OUT%\derived\pro_shop_pavilion_v1.fbx" --with-collision "%OUT%\derived\pro_shop_pavilion_v1_collision.fbx" > "%OUT%\logs\export.log" 2>&1
echo export exit %ERRORLEVEL% >> "%OUT%\logs\pipeline.log"
if "%CONCEPT%"=="" (
  python "%SRC%contact_sheet.py" --previews "%OUT%\previews" --output "%OUT%\previews\contact_sheet.png" > "%OUT%\logs\contact.log" 2>&1
) else (
  python "%SRC%contact_sheet.py" --previews "%OUT%\previews" --output "%OUT%\previews\contact_sheet.png" --concept "%CONCEPT%" > "%OUT%\logs\contact.log" 2>&1
)
echo contact exit %ERRORLEVEL% >> "%OUT%\logs\pipeline.log"
echo END %DATE% %TIME% >> "%OUT%\logs\pipeline.log"
endlocal
