import requests
import time
import subprocess

def run_test():
    # 1. Start the 10-driver fleet (Run simulate_fleet.py in background)
    print("Starting Fleet...")
    # (Assume simulate_fleet.py is already running in another terminal)

    time.sleep(5) # Wait for drivers to appear on map

    # 2. Simulate Rider Request
    print("Rider requesting ride...")
    ride_res = requests.post("http://localhost:8000/trip/create", json={
        "rider_id": "rider_1",
        "source": {"type": "Point", "coordinates": [74.74, 13.34]},
        "destination": {"type": "Point", "coordinates": [74.75, 13.35]}
    }).json()

    trip_id = ride_res.get("trip_id")
    driver_id = ride_res.get("assigned_driver")
    print(f"MATCHED: {driver_id} is now ORANGE (Locked) on map.")

    time.sleep(5) # Watch the orange marker move

    # 3. Driver Accepts
    print(f"Driver {driver_id} accepting...")
    requests.patch(f"http://localhost:8000/trip/accept/{trip_id}?driver_id={driver_id}")
    print(f"ACCEPTED: {driver_id} is now RED (Busy) on map.")

    time.sleep(10) # Watch them drive the customer

    # 4. Trip Ends
    print("Trip ending...")
    requests.put(f"http://localhost:8000/trip/{trip_id}/end?status=Completed")
    print(f"DONE: {driver_id} is now GREEN (Available) again.")

if __name__ == "__main__":
    run_test()