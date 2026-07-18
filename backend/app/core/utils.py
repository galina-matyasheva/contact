from __future__ import annotations


def anonymize_ip(ip: str) -> str:
    if not ip or ip == "unknown":
        return "unknown"
    parts = ip.split(".")
    if len(parts) == 4:
        parts[-2] = "0"
        parts[-1] = "0"
        return ".".join(parts)
    return ip
