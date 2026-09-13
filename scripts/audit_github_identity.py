#!/usr/bin/env python3
"""Fail closed if the current public source still names the retired GitHub identity."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OLD_OWNER = "Aletheia" + "-Prime"
OLD_PAGES = "aletheia" + "-prime.github.io"
OLD_REPO = "github.com/" + OLD_OWNER
FORBIDDEN = (OLD_OWNER, OLD_PAGES, OLD_REPO)

# Historical immutable evidence is not rewritten by this migration. There are
# currently no such files in the public source tree, so the allowlist is empty.
HISTORICAL_ALLOWLIST = set()

def main() -> int:
    hits = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if ".git" in rel.parts or rel.as_posix() in HISTORICAL_ALLOWLIST:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for token in FORBIDDEN:
            if token.casefold() in text.casefold():
                hits.append(f"{rel}: retired identity token")
                break
    if hits:
        print("GITHUB_IDENTITY_AUDIT_FAIL", file=sys.stderr)
        for hit in hits:
            print(" - " + hit, file=sys.stderr)
        return 1
    print("GITHUB_IDENTITY_AUDIT_PASS owner=navier-stokes-commons retired_current_refs=0 historical_allowlist=0")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
