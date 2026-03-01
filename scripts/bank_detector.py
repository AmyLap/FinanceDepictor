"""Bank detection utilities for uploaded statements.

The detect the bank for a PDF or OFX/QFX
statement so the upload flow can choose the correct parser class.

Functions:
- detect_pdf_bank(file_path) -> str: returns 'fnb', 'discovery', or 'unknown'
- detect_ofx_bank(file_path) -> str: similar, based on OFX headers
- detect_bank(file_path) -> str: convenience dispatcher by extension
"""
from __future__ import annotations

import re
from typing import Dict

import pdfplumber

# Lightweight keyword mapping. Expand as needed.
_BANK_KEYWORDS: Dict[str, tuple] = {
    "FNB": ("fnb", "first national bank", "first national", "fnb private"),
    "Discovery Bank": ("discovery", "discovery bank"),
}


def _match_keywords(text: str, mapping: Dict[str, tuple]) -> str:
    """Return the first bank id whose keyword appears in `text`.

    Matching is case-insensitive and looks for whole words or phrase fragments.
    """
    if not text:
        return "unknown"
    t = text.lower()
    for bank_id, keywords in mapping.items():
        for kw in keywords:
            if kw in t:
                return bank_id
    return "unknown"


def detect_pdf_bank(file_path: str) -> str:
    """Try to identify the bank from the first page text of a PDF.

    Returns a short id such as 'fnb', 'discovery', or 'unknown'.
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            # prefer first page (headers usually there)
            if len(pdf.pages) >= 1:
                page = pdf.pages[0]
                text = page.extract_text() or ""
            else:
                # fallback to entire document text
                text = "\n".join(p.extract_text() or "" for p in pdf.pages)
    except Exception:
        return "unknown"

    return _match_keywords(text, _BANK_KEYWORDS)


def detect_ofx_bank(file_path: str) -> str:
    """Try to identify the bank from OFX/QFX headers or early content.

    Reads the start of the file (it is text) and inspects tags like ORG,
    BANKID, or common bank-name substrings.
    """
    try:
        with open(file_path, "rb") as f:
            raw = f.read(8192)
        try:
            text = raw.decode("utf-8", errors="ignore")
        except Exception:
            text = str(raw)
    except Exception:
        return "unknown"

    # Search common OFX tags first
    # e.g. <ORG>FNB</ORG> or ORG:FNB in some flavors
    m = re.search(r"<ORG>([^<\n\r]+)", text, flags=re.IGNORECASE)
    if m:
        org = m.group(1).strip()
        res = _match_keywords(org, _BANK_KEYWORDS)
        if res != "unknown":
            return res

    # fallback to scanning the header/body for bank name fragments
    return _match_keywords(text, _BANK_KEYWORDS)


def detect_bank(file_path: str) -> str:
    """Convenience dispatcher: choose detection based on file extension."""
    lower = file_path.lower()
    if lower.endswith(".pdf"):
        return detect_pdf_bank(file_path)
    if lower.endswith(".ofx") or lower.endswith(".qfx") or lower.endswith(".xml"):
        return detect_ofx_bank(file_path)
    return "unknown"


__all__ = ["detect_pdf_bank", "detect_ofx_bank", "detect_bank"]
