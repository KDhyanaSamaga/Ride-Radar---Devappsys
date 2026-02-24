# Operations & Requirements

Documentation for project requirements, testing, and operational maintenance.

## 📋 Requirements

### Functional
- Users must be able to register and log in.
- The system must match a rider to the nearest driver within a 10km radius.
- Drivers must receive missions (Pickup/Drop-off) in real-time.
- The map must visualize all active drivers and their statuses.

### Non-Functional
- **Latency**: Driver matching via gRPC should complete in < 100ms.
- **Reliability**: Use Redis Distributed Locking to prevent race conditions.
- **Scalability**: Support at least 100 concurrent simulated drivers on a single instance.

## 🧪 Testing Strategy
- **Manual Verification**: Use the `simulate_fleet.py` script to generate load and verify map rendering.
- **Unit Tests**: Test utility functions (Fare calculation, distance math) in isolation.
- **Integration Tests**: Verify the gRPC loop between `main.py` and `geo_service.py`.

## 📊 Monitoring & Logging
- **FastAPI Logs**: stdout contains request/response logs and error stack traces.
- **gRPC Server**: Prints connection and method execution logs to the terminal.
- **Redis Monitor**: Use `redis-cli monitor` to watch geospatial updates and Pub/Sub messages in real-time.

## 🚢 Deployment Plan
1. **Containerization**: Use Docker to package the `API`, `Geo-Service`, `Redis`, and `MongoDB`.
2. **Orchestration**: Deploy via Docker Compose for local dev and Kubernetes for production.
3. **Environment**: Use `.env` files for production credentials and OSRM endpoint configuration.
