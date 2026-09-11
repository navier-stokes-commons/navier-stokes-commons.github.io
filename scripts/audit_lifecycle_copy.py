#!/usr/bin/env python3
"""Reject current-state copy that contradicts the canonical participation state."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from nsc_model import project_view

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
project = project_view()

# These are not a translation-quality oracle. They are contradiction tripwires for
# current public product surfaces when the canonical state says participation is open.
STALE_OPEN_BETA_PATTERNS = {
    "en": [r"\bpre[- ]?launch\b", r"\bbefore launch\b", r"\bnot yet launched\b"],
    "es": [r"\bprevia? al lanzamiento\b", r"\bantes del lanzamiento\b", r"\bprelanzamiento\b"],
    "pt-BR": [r"\bpré[- ]lançamento\b", r"\bantes do lançamento\b"],
    "fr": [r"\bpré[- ]lancement\b", r"\bavant le lancement\b"],
    "ar": [r"ما قبل الإطلاق", r"قبل الإطلاق"],
    "zh-Hans": [r"发布前", r"上线前"],
    "de": [r"\bvor dem start\b", r"\bvor der veröffentlichung\b"],
    "it": [r"\bpre[- ]lancio\b", r"\bprima del lancio\b"],
    "ru": [r"до запуска", r"до публикации"],
    "hi": [r"लॉन्च से पहले"],
    "bn": [r"লঞ্চের আগে"],
    "ja": [r"ローンチ前"],
    "ko": [r"출시 전"],
    "sw": [r"kabla ya uzinduzi"],
    "tr": [r"lansman öncesi", r"yayın öncesi"],
    "id": [r"pra[- ]peluncuran", r"sebelum peluncuran"],
}

errs: list[str] = []
if project.get("participation_status") == "open":
    for loc in project.get("locales", []):
        # Restrict the oracle to pages that speak in the product's present tense.
        for rel in (Path(loc) / "index.html", Path(loc) / "contribute" / "index.html"):
            path = PUBLIC / rel
            if not path.exists():
                errs.append(f"missing current-state surface {rel}")
                continue
            text = path.read_text(encoding="utf-8")
            for pat in STALE_OPEN_BETA_PATTERNS.get(loc, []):
                if re.search(pat, text, re.I):
                    errs.append(f"{rel}: open participation contradicted by stale launch copy /{pat}/")

if errs:
    print("LIFECYCLE_COPY_AUDIT_FAILED", file=sys.stderr)
    for err in errs:
        print(" - " + err, file=sys.stderr)
    raise SystemExit(1)
print(f"LIFECYCLE_COPY_AUDIT_PASS participation_status={project.get('participation_status')} locales={len(project.get('locales', []))}")
