def calculate_fare(distance, vehicle_type="Car"):
  
    pricing = {
        "Bike": {"base": 20.0, "per_km": 8.0},
        "Auto": {"base": 30.0, "per_km": 12.0},
        "Car":  {"base": 50.0, "per_km": 18.0},
        "Truck": {"base": 100.0, "per_km": 30.0}
    }
    
    config = pricing.get(vehicle_type, pricing["Car"])
    
    total_fare = config["base"] + (distance * config["per_km"])
    return round(total_fare, 2)