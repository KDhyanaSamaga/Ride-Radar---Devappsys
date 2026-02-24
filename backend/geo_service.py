import grpc
from concurrent import futures
import location_pb2
import location_pb2_grpc
from database.redis_client import r  

class GeoService(location_pb2_grpc.GeoServiceServicer):
    def FindNearestDriver(self, request, context):
        
        drivers = r.geosearch(
            "drivers_loc",
            longitude=request.lng,
            latitude=request.lat,
            radius=request.radius_km,
            unit="km",
            withdist=True,
            sort="ASC"
        )

        if not drivers:
            return location_pb2.DriverResponse(driver_id="", distance=0.0)

        
        closest_driver = drivers[0]
        
        return location_pb2.DriverResponse(
            driver_id=closest_driver[0],
            distance=float(closest_driver[1])
        )

def serve():
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    location_pb2_grpc.add_GeoServiceServicer_to_server(GeoService(), server)
    server.add_insecure_port('[::]:50051')
    
    print("Geo-Engine gRPC Server started on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()