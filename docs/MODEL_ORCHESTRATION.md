# Independent synthetic-review orchestration

The executor must use genuinely independent model families when its environment permits. Do not simulate independence by changing persona prompts on one model and calling them independent.

For each release-critical multi-reviewer criterion:
1. Run blind lanes before any prior verdict is exposed.
2. Use at least two materially distinct model families.
3. Prefer three independent development passes per family for defect discovery when compute permits; preserve all raw outputs.
4. Keep at least one held-out confirmation instance/family that was not used to tune the candidate.
5. Never aggregate a critical FAIL or P0/P1 veto into an average.
6. A reviewer unable to inspect its required modality must ABSTAIN.
7. After repairs, invalidate evidence affected by the changed pixels/runtime and recapture it.

The implementation agent may participate in diagnosis but cannot be the sole release reviewer.
