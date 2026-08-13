# Gate C2B3 run status

**Status:** `FULL_RESAMPLING_PENDING`

- Full outside-label candidate mapping: complete.
- Full 30,172-gene marker ranking: complete.
- Full 20-replicate graph-resampling stability: pending.
- Neutral-state freeze: not authorized.
- Disease/outcome unlock: not authorized.

Resume from the project root:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_gateC2B3_neutral_state_freeze.ps1 `
  -GateC2B2RunDir ".\phase17_v7\gateC2B2\20260812_full_representation" `
  -ResumeRunDir ".\phase17_v7\gateC2B3\20260813_full_neutral_state_freeze" `
  -Replicates 20 `
  -ResampleFraction 0.8
```

The runner will reuse the validated mapping and marker checkpoints.
