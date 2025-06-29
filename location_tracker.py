import geocoder

def get_live_location():
    g = geocoder.ip('me')
    if g.ok:
        lat, lng = g.latlng
        location_url = f"https://maps.google.com/?q={lat},{lng}"
        print("📍 Location Detected:", location_url)
        return location_url
    else:
        print("❌ Unable to get location")
        return None
