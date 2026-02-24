from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime
import grpc
from database.connection import db
from .geo_route import broadcast_status  # Import the broadcaster
import location_pb2
import location_pb2_grpc
from database.redis_client import r, lock_driver, unlock_driver
import json
from utils.osrm import get_osrm_route
from utils.cost import calculate_fare

router = APIRouter(prefix="/trip", tags=["trips"])

channel = grpc.insecure_channel('localhost:50051')
geo_stub = location_pb2_grpc.GeoServiceStub(channel)


@router.post("/create")
async def create_trip(trip_data: dict):
    trip_data["status"] = "Requested"
    trip_data["created_at"] = datetime.utcnow().isoformat() 

    try:
        lng = trip_data['source']['coordinates'][0]
        lat = trip_data['source']['coordinates'][1]

        request = location_pb2.FindNearestRequest(
            lat=lat, lng=lng, radius_km=10.0
        )
        response = geo_stub.FindNearestDriver(request)

        if not response.driver_id:
            db.trips.insert_one(trip_data)
            raise HTTPException(status_code=404, detail="No drivers found nearby")

        if lock_driver(response.driver_id):
            trip_data["driver_id"] = response.driver_id
            trip_data["status"] = "Driver_Assigned" # Simplified for demo
            
            # 1. Get Driver Location for Pickup Route
            driver_pos = r.geopos("drivers_loc", response.driver_id)
            pickup_route_data = None
            if driver_pos and driver_pos[0]:
                d_lng, d_lat = driver_pos[0]
                pickup_route_data = get_osrm_route((d_lat, d_lng), (lat, lng))

            # 2. Get Trip Route (User to Destination)
            source_coords = (lat, lng)
            dest_coords = (trip_data['destination']['coordinates'][1], trip_data['destination']['coordinates'][0])
            trip_route_data = get_osrm_route(source_coords, dest_coords)
            
            if trip_route_data:
                trip_data["distance_km"] = round(trip_route_data["distance_km"], 2)
                trip_data["fare"] = calculate_fare(trip_data["distance_km"], trip_data.get("vehicle_type", "Car"))
                trip_data["route_points"] = trip_route_data["coordinates"]
            
            result = db.trips.insert_one(trip_data)
            trip_id = str(result.inserted_id)
            
            # Send mission to driver: Go pick up user
            mission = {
                "driver_id": response.driver_id,
                "trip_id": trip_id,
                "action": "PICKUP",
                "destination": [lat, lng]
            }
            r.publish("driver_missions", json.dumps(mission))
            
            await broadcast_status(response.driver_id, "LOCKED")
            
            # Broadcast MATCH_MADE with both routes
            await broadcast_status(response.driver_id, "MATCH_MADE", {
                "user_id": trip_data.get("user_id", "unknown"),
                "pickup_route": pickup_route_data["coordinates"] if pickup_route_data else [],
                "trip_route": trip_route_data["coordinates"] if trip_route_data else []
            })
            
            return {
                "message": "Driver matched and locked!",
                "trip_id": trip_id,
                "assigned_driver": response.driver_id,
                "distance_km": trip_data.get("distance_km", 0),
                "fare": trip_data.get("fare", 0)
            }
        else:
            raise HTTPException(status_code=409, detail="Nearest driver is busy being matched")

    except grpc.RpcError:
        raise HTTPException(status_code=503, detail="Geo-Engine Service is offline")


@router.patch("/accept/{trip_id}")
async def accept_trip(trip_id: str, driver_id: str):
    trip = db.trips.find_one({"_id": ObjectId(trip_id), "driver_id": driver_id})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip proposal not found")

    db.trips.update_one(
        {"_id": ObjectId(trip_id)},
        {"$set": {"status": "Driver_Assigned", "accepted_at": datetime.utcnow().isoformat()}}
    )
    db.drivers.update_one({"_id": ObjectId(driver_id)}, {"$set": {"is_available": False}})
    
    unlock_driver(driver_id)
    
    
    await broadcast_status(driver_id, "BUSY")
    
    return {"message": "Trip accepted"}

@router.patch("/decline/{trip_id}")
async def decline_trip(trip_id: str, driver_id: str):
    db.trips.update_one(
        {"_id": ObjectId(trip_id)},
        {"$set": {"status": "Requested", "driver_id": None}}
    )
    unlock_driver(driver_id)
    
  
    await broadcast_status(driver_id, "AVAILABLE")
    
    return {"message": "Trip declined"}


@router.put("/{trip_id}/start")
async def start_trip(trip_id: str):
    trip = db.trips.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    db.trips.update_one(
        {"_id": ObjectId(trip_id), "status": "Driver_Assigned"},
        {"$set": {"status": "Ongoing", "started_at": datetime.utcnow().isoformat()}}
    )
    
    # Send mission to driver: Go to destination
    mission = {
        "driver_id": trip["driver_id"],
        "trip_id": trip_id,
        "action": "DROP_OFF",
        "destination": [trip['destination']['coordinates'][1], trip['destination']['coordinates'][0]]
    }
    r.publish("driver_missions", json.dumps(mission))
    
    await broadcast_status(trip["driver_id"], "BUSY")
    
    return {"message": "Trip started"}


@router.put("/{trip_id}/end")
async def end_trip(trip_id: str, status: str):
    if status not in ["Completed", "Cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    trip = db.trips.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    update_fields = {"status": status, "ended_at": datetime.utcnow().isoformat()}

    if status == "Completed":
        try:
            dist = calculate_distance(
                trip['source']['coordinates'][1], trip['source']['coordinates'][0],
                trip['destination']['coordinates'][1], trip['destination']['coordinates'][0]
            )
            driver = db.drivers.find_one({"_id": ObjectId(trip["driver_id"])})
            v_type = driver.get("vehicle_type", "Car") if driver else "Car"
            update_fields["distance_km"] = round(dist, 2)
            update_fields["fare"] = calculate_fare(dist, v_type)
        except Exception as e:
            print(f"Fare Error: {e}")

    db.trips.update_one({"_id": ObjectId(trip_id)}, {"$set": update_fields})
    
    if trip.get("driver_id"):
        driver_id = trip["driver_id"]
        # Only update DB if it's a valid MongoDB ObjectId
        if len(driver_id) == 24 and all(c in "0123456789abcdefABCDEF" for c in driver_id):
            db.drivers.update_one({"_id": ObjectId(driver_id)}, {"$set": {"is_available": True}})
        
        # Always unlock in Redis and broadcast status for the map
        unlock_driver(driver_id)
        await broadcast_status(driver_id, "AVAILABLE")
    
    return {"message": f"Trip {status}", "fare": update_fields.get("fare", 0)}


@router.get("/history/{role}/{id}")
async def get_history(role: str, id: str):
    query_key = "user_id" if role == "user" else "driver_id"
    trips = list(db.trips.find({query_key: id}))
    for t in trips:
        t["_id"] = str(t["_id"])
    return {"history": trips}