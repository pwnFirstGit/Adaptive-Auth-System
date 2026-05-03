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
    
    import requests

def get_location_from_ip(ip_address: str) -> dict:
    """
    Get location and coordinates from IP address.
    Returns dict with location, latitude, longitude.
    """
    try:
        if ip_address in ("127.0.0.1", "localhost", "::1"):
            return {
                "location": "local",
                "latitude": None,
                "longitude": None
            }

        response = requests.get(
            f"http://ip-api.com/json/{ip_address}",
            timeout=3
        )
        data = response.json()

        if data.get("status") == "success":
            return {
                "location":  f"{data.get('city', 'unknown')}, {data.get('country', 'unknown')}",
                "latitude":  data.get("lat"),
                "longitude": data.get("lon")
            }

        return {"location": "unknown", "latitude": None, "longitude": None}

    except Exception:
        return {"location": "unknown", "latitude": None, "longitude": None}