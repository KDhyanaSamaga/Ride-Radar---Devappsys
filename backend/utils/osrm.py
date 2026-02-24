import requests
import json

def get_osrm_route(start: tuple, end: tuple):
    """
    start: (lat, lng)
    end: (lat, lng)
    Returns: { 'distance_km': float, 'duration_sec': float, 'coordinates': [[lat, lng], ...] }
    """
    url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=geojson"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data['code'] == 'Ok':
            route = data['routes'][0]
            # OSRM returns [lng, lat], we want [lat, lng] for Leaflet/internal use consistency if preferred, 
            # but let's stick to [lat, lng] as per our usual logic.
            coords = [[p[1], p[0]] for p in route['geometry']['coordinates']]
            
            return {
                "distance_km": route['distance'] / 1000.0,
                "duration_sec": route['duration'],
                "coordinates": coords
            }
    except Exception as e:
        print(f"OSRM Error: {e}")
    
    return None
