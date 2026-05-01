import hashlib
from fastapi import Request

def get_device_info(request: Request) -> dict:
    """
    Extract device information from request headers.
    Returns both human-readable info and a hash fingerprint.
    """
    user_agent = request.headers.get("user-agent", "unknown")

    # ── Parse OS ──
    if "Windows" in user_agent:
        os = "Windows"
    elif "Macintosh" in user_agent or "Mac OS" in user_agent:
        os = "MacOS"
    elif "iPhone" in user_agent or "iPad" in user_agent:
        os = "iOS"
    elif "Android" in user_agent:
        os = "Android"
    elif "Linux" in user_agent:
        os = "Linux"
    else:
        os = "Unknown OS"

    # ── Parse Browser ──
    if "Chrome" in user_agent and "Edg" not in user_agent:
        browser = "Chrome"
    elif "Firefox" in user_agent:
        browser = "Firefox"
    elif "Safari" in user_agent and "Chrome" not in user_agent:
        browser = "Safari"
    elif "Edg" in user_agent:
        browser = "Edge"
    elif "curl" in user_agent:
        browser = "curl"
    else:
        browser = "Unknown Browser"

    # ── Create readable label ──
    device_label = f"{browser}_{os}"  # e.g. "Chrome_MacOS"

    # ── Hash it for DB storage ──
    device_hash = hashlib.md5(device_label.encode()).hexdigest()

    return {
        "device_label": device_label,   # human readable
        "device_hash":  device_hash      # stored in DB
    }