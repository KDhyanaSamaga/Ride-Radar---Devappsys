from fastapi import FastAPI
# Fixed the import syntax here
from routes.user_routes import router as user_router 
from routes.driver_route import router as driver_route
from routes.trip_route import router as trip_route
from routes.geo_route import router as geo_route 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="My Ride-Sharing App")

app.add_middleware(CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router)
app.include_router(driver_route)
app.include_router(trip_route)
app.include_router(geo_route)

@app.get("/")
def root():
    return {"message": "Welcome to the API"}