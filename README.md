# Ride-Radar 🚖

A distributed, real-time ride-sharing system built with FastAPI, gRPC, and Redis Geospatial.

## 📖 Project Overview

### Goal
Ride-Radar aims to provide a high-performance, low-latency infrastructure for ride-hailing services. The primary goal is to demonstrate how microservices can handle high-frequency geospatial updates and matching at scale.

### Scope
- **Real-time Tracking**: Dynamic driver positioning on a live map.
- **Geospatial Matching**: Efficiently finding the nearest available driver using gRPC and Redis.
- **Trip Lifecycle**: Managing the flow from trip request to completion.
- **Simulation**: Tools to simulate entire fleets of drivers for stress testing and demos.

### Users
- **Riders**: Users who request rides to a specific destination.
- **Drivers**: Service providers who receive missions and navigate to users.
- **Administrators**: Monitoring the fleet status and system health via the map visualization.

## 🚀 Tech Stack
- **Backend**: Python, FastAPI (REST & WebSockets), gRPC (Service Communication)
- **Data**: MongoDB (Persistence), Redis (Geo-Indexing & Pub/Sub)
- **Frontend**: Vanilla HTML/JS, Leaflet.js
- **Routing**: OSRM (Open Source Routing Machine)

## 🛠️ Local Setup & Development

### Prerequisites
- Python 3.9+
- MongoDB (Running on `localhost:27017`)
- Redis (Running on `localhost:6379`)
- OSRM Backend (Uses `router.project-osrm.org` by default)

### Installation
1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd "Final+Final"
   ```

2. **Setup Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### Running the Services
1. **Start the Geo-Service (gRPC)**:
   ```bash
   python geo_service.py
   ```
2. **Start the Main API (FastAPI)**:
   ```bash
   uvicorn main:app --reload
   ```
3. **Open the Map**:
   Simply open `frontend/map.html` in a modern web browser.

## ⚙️ Configuration & Environment Variables
Currently, the app uses default local connections. You can modify the following in `database/connection.py` and `database/redis_client.py`:
- `MONGODB_URI`: Default `mongodb://localhost:27017/`
- `REDIS_HOST`: Default `localhost`
- `gRPC_PORT`: Default `50051`

## ⚠️ Known Limitations & Future Improvements
- **Security**: Current version uses basic authentication; production requires JWT/OAuth2.
- **Scaling**: The WebSocket broadcaster currently uses an in-memory `set`; for production, use Redis Pub/Sub for scale.
- **UI**: The frontend is a single-page demo; requires a full React/Mobile implementation for product use.
