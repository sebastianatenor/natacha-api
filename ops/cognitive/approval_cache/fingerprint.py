# ops/cognitive/approval_cache/fingerprint.py

import hashlib


def proposal_fingerprint(
    text: str,
    intent: str,
    risk: str,
    domains: list[str],
) -> str:
    base = "|".join(
        [
            intent or "",
            risk or "",
            ",".join(sorted(domains or [])),
            text.lower().strip(),
        ]
    )

    return hashlib.sha256(base.encode("utf-8")).hexdigest()
