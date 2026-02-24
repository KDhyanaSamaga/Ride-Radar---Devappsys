# Ride-Radar 🚖

A distributed, real-time ride-sharing system built with FastAPI, gRPC, and Redis Geospatial.

## 🌟 Features
- **Real-time Driver Tracking**: Geospatial indexing using Redis `GEO` commands.
- **Fast Driver Matching**: Low-latency matching via gRPC-based Geo-Service.
- **Microservices Architecture**: Separate concerns for Business logic and Geospatial operations.
- **Dynamic Routing**: Integration with OSRM for accurate trip routes and fares.
- **Interactive Map**: Frontend visualization using Leaflet.js and WebSockets.

## 🚀 Tech Stack
- **Backend**: Python, FastAPI, gRPC, Cerberus (Validation)
- **Database**: MongoDB (Persistence), Redis (Geospatial Indexing & Pub/Sub)
- **Frontend**: Vanilla HTML/JS, Leaflet.js
- **Tooling**: OSRM (Open Source Routing Machine)

## 🛠️ Quick Start

### Prerequisites
- Python 3.9+
- MongoDB
- Redis
- [OSRM Backend](http://project-osrm.org/) (External or Local)

### Setup
1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd "Final+Final"
   ```

2. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Start Services**:
   - **Geo Service (gRPC)**:
     ```bash
     python geo_service.py
     ```
   - **Main API (FastAPI)**:
     ```bash
     uvicorn main:app --reload
     ```

4. **Run Simulations** (Optional):
   ```bash
   python simulate_fleet.py
   ```

5. **Open Frontend**:
   Open `frontend/map.html` in your browser.

## 📄 License
MIT
