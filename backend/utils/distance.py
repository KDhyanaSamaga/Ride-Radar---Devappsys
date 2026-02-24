import math
from .osrm import get_osrm_route

def calculate_distance(lat1, lon1, lat2, lon2, use_osrm=False):
    """
    Calculates the distance between two points.
    Defaults to Haversine, but can use OSRM for road distance.
    """
    if use_osrm:
        route_data = get_osrm_route((lat1, lon1), (lat2, lon2))
        if route_data:
            return round(route_data['distance_km'], 2)

    # Radius of the Earth in kilometers
    R = 6371.0
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)

