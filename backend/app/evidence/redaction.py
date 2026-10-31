"""Mask common credential formats in metadata. This is not a complete secret scanner."""
import re

PATTERNS = [
    re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b'),
    re.compile(r'\b(?:sk-[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16})\b'),
    re.compile(r'(?i)(https?://)[^\s/@:]+:[^\s/@]+@'),
]

def redact(value):
    if isinstance(value, str):
        for pattern in PATTERNS:
            value = pattern.sub('[REDACTED]', value)
        return value
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, dict):
        # Keep paths and identifiers intact for source citation validation; content is never returned.
        return {k: v if k in ('id', 'source', 'target', 'file', 'sha256', 'evidence_ids', 'support_edge_ids') else redact(v) for k,v in value.items()}
    return value
