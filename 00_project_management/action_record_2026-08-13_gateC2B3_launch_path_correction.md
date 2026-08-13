# Action record: Gate C2B3 launch-path correction

**Date:** 13 August 2026

## Reported problem

The Gate C2B3 command was launched from `C:\Users\Administrator` while using the
relative script path `.\audit_tools\run_6013RP_phase17_gateC2B3_neutral_state_freeze.ps1`.
PowerShell therefore searched under the current C-drive directory and correctly
reported that the script did not exist there.

## Verification

The requested runner exists at:

`H:\cuhk-2025fALL\6013RP-wyf\audit_tools\run_6013RP_phase17_gateC2B3_neutral_state_freeze.ps1`

Verified file size: 8,014 bytes before this path-resolution correction.

## Corrective action

The runner was changed so a relative `-ResumeRunDir` is always resolved against
the detected project root rather than the caller's current PowerShell directory.
This makes an absolute script invocation safe from any working directory. The
existing `-GateC2B2RunDir` already followed this project-root rule.

## Correct launch contract

The preferred command uses absolute paths and therefore does not depend on the
current PowerShell location:

```powershell
powershell -ExecutionPolicy Bypass `
  -File "H:\cuhk-2025fALL\6013RP-wyf\audit_tools\run_6013RP_phase17_gateC2B3_neutral_state_freeze.ps1" `
  -GateC2B2RunDir "H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC2B2\20260812_full_representation" `
  -ResumeRunDir "H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC2B3\20260813_full_neutral_state_freeze" `
  -Replicates 20 `
  -ResampleFraction 0.8
```

The alternative is to run `Set-Location H:\cuhk-2025fALL\6013RP-wyf` before the
previous relative-path command.

## Scientific state

No scientific file, representation, marker result or candidate-mapping decision
was changed. Gate C2B2 remains passed, Gate C2B3 full resampling remains pending,
and disease/outcome metadata remains locked.
