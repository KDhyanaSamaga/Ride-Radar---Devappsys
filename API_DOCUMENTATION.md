# API Documentation

## 🌐 REST Endpoints (FastAPI)

### User Routes (`/user`)
- `POST /user/register`: Register a new user.
- `POST /user/login`: Authenticate and get a session.

### Driver Routes (`/driver`)
- `POST /driver/register`: Register a driver with vehicle details.
- `GET /driver/status/{id}`: Get current online status.

### Trip Routes (`/trip`)
- `POST /trip/create`: Create a trip request.
  - **Body**: `{ "source": {...}, "destination": {...}, "vehicle_type": "Car" }`
- `PUT /trip/{id}/start`: Mark a trip as ongoing.
- `PUT /trip/{id}/end`: Complete a trip.
- `GET /trip/history/{role}/{id}`: Retrieve trip history for a user or driver.

### Geo Routes (`/geo`)
- `WS /geo/ws/{client_id}`: WebSocket connection for receiving real-time driver updates.

---

## 🛰️ gRPC Interface (Geo-Service)

**Port**: `50051`

### Methods

#### `FindNearestDriver`
- **Request**: `FindNearestRequest (lat, lng, radius_km)`
- **Response**: `DriverResponse (driver_id, distance)`

#### `UpdateLocation`
- **Request**: `UpdateLocationRequest (driver_id, lat, lng)`
- **Response**: `SimpleResponse (success)`
