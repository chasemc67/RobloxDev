# usage: run.sh Py Tag  (args file must already be on PC)
ssh pc "schtasks /create /tn 3dmb_aa3_$2 /tr \"powershell -NoProfile -ExecutionPolicy Bypass -File C:\\Users\\chase\\aa_fix3\\job.ps1 -Py $1 -Tag $2\" /sc once /st 23:59 /f >\$null; schtasks /run /tn 3dmb_aa3_$2"
