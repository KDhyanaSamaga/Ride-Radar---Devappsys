import asyncio
import asyncio
import httpx
import random

BASE_URL = "http://localhost:8000/trip"
USERS = ["user_fixed_1", "user_fixed_2", "user_fixed_3", "sim_rider_4", "sim_rider_5"]

async def simulate_ride_lifecycle(user_id):
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        source_lat = 13.34 + random.uniform(-0.01, 0.01)
        source_lng = 74.74 + random.uniform(-0.01, 0.01)
        
        print(f"🚀 {user_id} requesting a ride...")
        payload = {
            "user_id": user_id,
            "source": {"type": "Point", "coordinates": [source_lng, source_lat]},
            "destination": {"type": "Point", "coordinates": [source_lng+0.01, source_lat+0.01]}
        }
        
        try:
            res = await client.post(f"{BASE_URL}/create", json=payload)
            
            if res.status_code == 409:
                print(f"⚠️ {user_id}: Driver was busy (Lock engaged).")
                return
            elif res.status_code != 200:
                print(f"❌ {user_id} Error: {res.text}")
                return

            data = res.json()
            trip_id = data['trip_id']
            driver_id = data['assigned_driver']
            print(f"🟠 MATCHED: {user_id} -> {driver_id} (Locked/Orange)")

            
            await asyncio.sleep(3)
            await client.patch(f"{BASE_URL}/accept/{trip_id}", params={"driver_id": driver_id})
            print(f"🔴 ACCEPTED: {driver_id} is now BUSY (Red)")

            
            await asyncio.sleep(10)

            
            await client.put(f"{BASE_URL}/end", params={"trip_id": trip_id, "status": "Completed"})
            print(f"🟢 COMPLETED: {driver_id} is now AVAILABLE (Green)")

        except Exception as e:
            print(f"❌ Connection error for {user_id}: {e}")

async def main():
    print(f"--- Starting Continuous Multi-Rider Simulation ---")
    iteration = 1
    while True:
        print(f"\n--- Batch Iteration {iteration} ---")
        
        await asyncio.gather(*(simulate_ride_lifecycle(u) for u in USERS))
        
        print(f"\n--- Batch {iteration} complete. Restarting in 5 seconds... ---")
        await asyncio.sleep(5) 
        iteration += 1

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")