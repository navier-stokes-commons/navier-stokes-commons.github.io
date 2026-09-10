from __future__ import annotations
import os
from pathlib import Path

class ScratchPolicyError(RuntimeError):
    pass

def _system_ram_root() -> Path | None:
    # Construct the conventional Linux shared-memory path from components so
    # host-specific absolute paths never become serialized public state.
    candidate=Path('/')/'dev'/'shm'
    return candidate if candidate.is_dir() and os.access(candidate,os.W_OK) else None

def _reject_system_temp(path: Path) -> None:
    parts=path.absolute().parts
    if len(parts)>1 and parts[1].lower()=='tmp':
        raise ScratchPolicyError('system temporary directory is prohibited for audit scratch')

def scratch_dir(purpose: str, *, primary_env: str='NSC_AUDIT_SCRATCH') -> Path:
    """Return a disposable audit directory without persisting its host path in receipts.

    Precedence: purpose-specific environment, shared audit environment, CI runner
    scratch, Linux RAM-backed scratch. The caller owns only the returned child.
    """
    bases=[]
    for name in (primary_env,'NSC_AUDIT_SCRATCH','RUNNER_TEMP'):
        value=os.getenv(name,'').strip()
        if value:
            bases.append(Path(value).expanduser())
    if not bases:
        ram=_system_ram_root()
        if ram is not None: bases.append(ram)
    if not bases:
        raise ScratchPolicyError('no approved scratch root; set NSC_AUDIT_SCRATCH')
    base=bases[0]
    _reject_system_temp(base)
    out=base/f'nsc-{purpose}'
    out.mkdir(parents=True,exist_ok=True)
    return out
