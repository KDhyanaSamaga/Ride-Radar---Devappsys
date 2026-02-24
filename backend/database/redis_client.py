import redis

REDIS_HOST = 'redis-12302.crce276.ap-south-1-3.ec2.cloud.redislabs.com'
REDIS_PORT = 12302
REDIS_PASSWORD = 'jUt3JD55bZcFHohvrNc1eb8H3sNnxqh5' 

pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True,
    max_connections=25 
)

r = redis.Redis(connection_pool=pool)

def test_redis():
    try:
        return r.ping()
    except Exception as e:
        print(f"Redis Cloud Error: {e}")
        return False
    
def update_driver_location(driver_id, lat, lng):
   
    return r.geoadd("drivers_loc", (lng, lat, driver_id))

def find_nearby_drivers(lat, lng, radius_km=5):
    
    return r.geosearch(
        "drivers_loc",
        longitude=lng,
        latitude=lat,
        radius=radius_km,
        unit="km",
        withdist=True
    )

def lock_driver(driver_id, expiry_sec=30):
    
    return r.set(f"lock:{driver_id}", "busy", ex=expiry_sec, nx=True)

def unlock_driver(driver_id):
    
    return r.delete(f"lock:{driver_id}")