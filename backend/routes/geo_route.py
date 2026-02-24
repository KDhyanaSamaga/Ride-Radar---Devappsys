from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from database.redis_client import r  
import json

router = APIRouter(prefix="/geo", tags=["Geo-Location"])

map_clients = set()

async def broadcast_status(id_str: str, msg_type: str, extra_data: dict = None):
    payload = {
        "type": msg_type,
    }
    
    if msg_type == "STATUS_UPDATE":
        payload.update({"driver_id": id_str, "status": extra_data.get("status") if extra_data else "AVAILABLE"})
    elif msg_type == "RIDER_REQUEST":
        payload.update({"user_id": id_str, "lat": extra_data['lat'], "lng": extra_data['lng']})
    elif msg_type == "RIDER_PICKUP":
        payload.update({"user_id": id_str})
    
    # Generic relay for other types like MATCH_MADE
    if extra_data:
        payload.update(extra_data)

    for client in list(map_clients):
        try:
            await client.send_text(json.dumps(payload))
        except:
            if client in map_clients:
                map_clients.remove(client)

@router.websocket("/ws/map")
async def map_visualization_websocket(websocket: WebSocket):
    """Broadcaster: Sends updates to the browser map."""
    await websocket.accept()
    map_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text() 
    except WebSocketDisconnect:
        map_clients.remove(websocket)

@router.websocket("/ws/location/{driver_id}")
async def driver_location_websocket(websocket: WebSocket, driver_id: str):
    """Receiver: Gets GPS data from the driver simulator and broadcasts to map."""
    await websocket.accept()
    print(f"Driver {driver_id} connected to stream.")
    
    try:
        while True:
            data = await websocket.receive_text()
            location = json.loads(data)
   
            r.geoadd("drivers_loc", (location['lng'], location['lat'], driver_id))

            broadcast_payload = json.dumps({
                "type": "LOCATION",
                "driver_id": driver_id,
                "lat": location['lat'],
                "lng": location['lng'],
                "status": location.get('status', 'AVAILABLE'),
                "arrived": location.get('arrived', False)
            })
            
            for client in list(map_clients):
                try:
                    await client.send_text(broadcast_payload)
                except:
                    map_clients.remove(client)
            
    except WebSocketDisconnect:
        print(f"Driver {driver_id} disconnected.")