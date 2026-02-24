import asyncio
import websockets
import json
import random
import redis
import sys
import os
import redis.asyncio as aioredis  

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.osrm import get_osrm_route
from database.redis_client import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

DRIVERS = [f"driver_{i}" for i in range(101, 106)]  # Use 5 drivers for demo as requested

LAT_MIN, LAT_MAX = 12.85, 12.95
LNG_MIN, LNG_MAX = 74.80, 74.90

class SimulatorDriver:
    def __init__(self, driver_id):
        self.driver_id = driver_id
        self.lat = random.uniform(LAT_MIN, LAT_MAX)
        self.lng = random.uniform(LNG_MIN, LNG_MAX)
        self.state = "IDLE"  
        self.route = []
        self.target_trip_id = None
        self.websocket = None

    async def run(self):
        uri = f"ws://localhost:8000/geo/ws/location/{self.driver_id}"
    
        asyncio.create_task(self.listen_for_missions())

        arrived_notified = False

        while True:
            try:
                async with websockets.connect(uri) as ws:
                    self.websocket = ws
                    print(f"{self.driver_id} is now ONLINE.")
                    
                    while True:
                        await self.update_position()
                        
                        # Detect arrival at user
                        notice = False
                        if self.state == "PICKING_UP" and not self.route and not arrived_notified:
                            notice = True
                            arrived_notified = True
                        elif self.state != "PICKING_UP":
                            arrived_notified = False

                        payload = {
                            "lat": round(self.lat, 6),
                            "lng": round(self.lng, 6),
                            "status": self.state,
                            "arrived": notice
                        }
                        
                        await ws.send(json.dumps(payload))
                        await asyncio.sleep(1) # Faster updates
            except Exception as e:
                print(f"Connection lost for {self.driver_id}: {e}")
                await asyncio.sleep(5)

    async def update_position(self):
        if self.state == "IDLE":
           
            self.lat += random.uniform(-0.001, 0.001) 
            self.lng += random.uniform(-0.001, 0.001)
            
         
            self.lat = max(LAT_MIN, min(LAT_MAX, self.lat))
            self.lng = max(LNG_MIN, min(LNG_MAX, self.lng))
            
        elif self.state in ["PICKING_UP", "ON_TRIP"]:
            if self.route:
                steps = min(10, len(self.route))
                for _ in range(steps):
                    next_pt = self.route.pop(0)
                    self.lat, self.lng = next_pt[0], next_pt[1]
                
                if not self.route:
                    # Arrived at destination/user
                    if self.state == "PICKING_UP":
                        print(f"{self.driver_id} reached user. Waiting for trip start.")
                        
                        pass 
                    else:
                        print(f"{self.driver_id} reached destination. Back to IDLE.")
                        self.state = "IDLE"
                        self.target_trip_id = None

    async def listen_for_missions(self):
        r_async = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)
        pubsub = r_async.pubsub()
        await pubsub.subscribe("driver_missions")
        
        print(f"{self.driver_id} listening for missions...")
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                if data.get('driver_id') == self.driver_id:
                    action = data.get('action') 
                    dest = data.get('destination') 
                    
                    print(f"{self.driver_id} received mission: {action} to {dest}")
                    
                    # Fetch route from OSRM
                    route_data = get_osrm_route((self.lat, self.lng), (dest[0], dest[1]))
                    if route_data:
                        self.route = route_data['coordinates']
                        self.state = "PICKING_UP" if action == "PICKUP" else "ON_TRIP"
                        self.target_trip_id = data.get('trip_id')
                    else:
                        
                        self.route = [dest]
                        self.state = "PICKING_UP" if action == "PICKUP" else "ON_TRIP"

async def main():
    print(f"--- Starting Advanced Fleet Simulation ---")
    drivers = [SimulatorDriver(d) for d in DRIVERS]
    await asyncio.gather(*(d.run() for d in drivers))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nFleet simulation stopped.")