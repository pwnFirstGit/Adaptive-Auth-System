import requests

def get_location_from_ip(ip_address: str) -> str:
    """
    Get country from IP address using free ip-api.com
    Returns location string like 'India' or 'unknown'
    """
    try:
        # Skip for localhost/private IPs
        if ip_address in ("127.0.0.1", "localhost", "::1"):
            return "local"

        response = requests.get(
            f"http://ip-api.com/json/{ip_address}",
            timeout=3  # don't slow down login if API is down
        )
        data = response.json()

        if data.get("status") == "success":
            country = data.get("country", "unknown")
            city    = data.get("city", "unknown")
            return f"{city}, {country}"
        return "unknown"

    except Exception:
        return "unknown"  # never crash login because of geo failure