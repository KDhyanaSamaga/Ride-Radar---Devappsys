from fastapi import APIRouter, HTTPException
from bson import ObjectId
from database.connection import db
from secure import hash_password, verify_password
from schema import driver_validator, driver_schema
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from database.redis_client import update_driver_location


router = APIRouter(prefix="/driver", tags=["driver"])

# Helper to clean data (removes password and converts ObjectId)
def clean_driver_data(driver):
    if driver:
        driver["_id"] = str(driver["_id"])
        if "password" in driver:
            del driver["password"]
    return driver

@router.post("/signup")
def driver_signup(data: dict):
    
    if not driver_validator.validate(data):
        raise HTTPException(status_code=400, detail=driver_validator.errors)
    
    
    email = data["email"].lower()
    if db.drivers.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Driver already registered with this email")
    
    
    data["email"] = email
    data["password"] = hash_password(data["password"])
    data["created_at"] = datetime.utcnow().isoformat()
    data["is_available"] = True  
    
    
    inserted = db.drivers.insert_one(data)
    
    return {
        "message": "Driver signup successful",
        "_id": str(inserted.inserted_id)
    }

@router.post("/login")
def driver_login(data: dict):
    email = data.get("email", "").lower()
    password = data.get("password", "")
    
    driver = db.drivers.find_one({"email": email})
    
    if not driver or not verify_password(password, driver["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {
        "message": "Login successful",
        "driver": clean_driver_data(driver)
    }

@router.get("/{driver_id}/profile")
def driver_profile(driver_id: str):
    try:
        driver = db.drivers.find_one({"_id": ObjectId(driver_id)})
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        return clean_driver_data(driver)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Driver ID format")

@router.put("/{driver_id}/profile")
def driver_profil_update(driver_id: str, data: dict):
    try:
        oid = ObjectId(driver_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Driver ID format")

   
    if not driver_validator.validate(data, update=True):
        raise HTTPException(status_code=400, detail=driver_validator.errors)

    
    forbidden = ["_id", "password", "email"]
    for field in forbidden:
        if field in data:
            del data[field]

    
    result = db.drivers.update_one({"_id": oid}, {"$set": data})
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Driver not found")

    updated_driver = db.drivers.find_one({"_id": oid})
    return {
        "message": "Profile updated",
        "driver": clean_driver_data(updated_driver)
    }

@router.websocket("/ws/driver/{driver_id}")
async def driver_location_stream(websocket: WebSocket, driver_id: str):
    await websocket.accept() 
    try:
        while True:
           
            data = await websocket.receive_json()
            
            update_driver_location(driver_id, data['lat'], data['lng'])
    except WebSocketDisconnect:
        print(f"Driver {driver_id} disconnected")