from fastapi import FastAPI, HTTPException, APIRouter
from bson import ObjectId
from database.connection import db
from secure import hash_password, verify_password
from schema import user_validator  

router = APIRouter(prefix="/user", tags=["Users"])

def clean_user_data(user):
    if user:
        user["_id"] = str(user["_id"])
        if "password" in user:
            del user["password"]
    return user

@router.post("/signup")
def user_signup(data: dict):
    if not user_validator.validate(data):
        raise HTTPException(
            status_code=400,
            detail=user_validator.errors
        )
    
    email = data["email"].lower()
    
    if db.users.find_one({"email": email}):
        raise HTTPException(
            status_code=400, 
            detail="User already present"
        )
    
    data["email"] = email
    data["password"] = hash_password(data["password"])
    inserted = db.users.insert_one(data)

    return {
        "message": "Sign up successful",
        "_id": str(inserted.inserted_id)
    }

@router.post("/login")
def user_login(data: dict):
    email = data.get("email", "").lower()
    password = data.get("password", "")

    user = db.users.find_one({"email": email})
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not present. Please sign up."
        )
    
    if not verify_password(password, user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Password did not match. Check again."
        )
    
    if "browser_id" in data:
        db.users.update_one(
            {"_id": user["_id"]}, 
            {"$set": {"browser_id": data["browser_id"]}}
        )
    
    return {
        "message": "Login successful",
        "_id": str(user["_id"]),
        "user_name": user["user_name"]
    }

@router.get("/{user_id}/profile")
def user_profile(user_id: str):
 
    try:
        result = db.users.find_one({"_id": ObjectId(user_id)})
        
        if not result:
            raise HTTPException(
                status_code=404, 
                detail="User not found"
            )
        
        return clean_user_data(result)
        
    except Exception:
        raise HTTPException(
            status_code=400, 
            detail="Invalid User ID format"
        )
    
@router.post("/{user_id}/profile")
def update_profile(user_id: str, data: dict):

    try:
        oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid User ID format")

    user = db.users.find_one({"_id": oid})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user_validator.validate(data, update=True):
        raise HTTPException(status_code=400, detail=user_validator.errors)


    protected_fields = ["_id", "password", "email"]
    for field in protected_fields:
        if field in data:
            del data[field]

    if data:
        db.users.update_one(
            {"_id": oid},
            {"$set": data}
        )


    updated_user = db.users.find_one({"_id": oid})
    updated_user["_id"] = str(updated_user["_id"])
    if "password" in updated_user:
        del updated_user["password"]

    return {
        "message": "Profile updated successfully",
        "user": updated_user
    }


@router.get("/browser/{browser_id}")
def get_profile_by_browser(browser_id: str):
    """
    Alternative route: Fetch profile using Browser ID 
    (Useful for auto-loading guest data or persistent sessions)
    """
    user = db.users.find_one({"browser_id": browser_id})
    if not user:
        raise HTTPException(status_code=404, detail="No profile linked to this browser")
    
    return clean_user_data(user)