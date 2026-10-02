# 🚛 Spotter ELD & HOS Commercial Trip Planner

An enterprise-grade full-stack Commercial Motor Vehicle (CMV) trip planning and Hours of Service (HOS) simulation platform built with **Django REST Framework** and **React (TypeScript & Material UI)**.

The system calculates realistic commercial highway routes, enforces **FMCSA 49 CFR Part 395 regulations (70-hour / 8-day rule for property-carrying drivers)**, and automatically generates pixel-perfect, 24-hour **Driver's Daily Log Sheets (RODS)** with continuous step-line graph grids, detailed remarks, and 70-hour recaps.

---

## 📋 Table of Contents
1. [Core Features & Deliverables](#-core-features--deliverables)
2. [HOS & Business Rules (FMCSA 49 CFR § 395)](#-hos--business-rules-fmcsa-49-cfr--395)
3. [Architecture & System Design](#-architecture--system-design)
4. [Tech Stack](#-tech-stack)
5. [Local Development & Setup](#-local-development--setup)
6. [API Specification](#-api-specification)
7. [Automated Testing Suite](#-automated-testing-suite)
8. [Live Deployment Guide](#-live-deployment-guide)
9. [3-5 Minute Loom Presentation Script](#-3-5-minute-loom-presentation-script)

---

## 🚀 Core Features & Deliverables

### 1. Trip Inputs
- **Current Location**: Starting point / origin terminal.
- **Pickup Location**: Shipper facility (automatically allocated **1.0 hour On-Duty Not Driving** for cargo loading, BOL signing, and pre-trip vehicle check).
- **Dropoff Location**: Consignee facility (automatically allocated **1.0 hour On-Duty Not Driving** for cargo unloading and final inspection).
- **Current Cycle Used (Hrs)**: Cumulative duty hours used in the preceding 7/8 days (0.0 to 70.0 hrs).
- **Quick Evaluation Presets**: One-click instant testing presets (e.g., *Chicago → Indy → Dallas*, *New York → Chicago → Los Angeles*, *Atlanta → Charlotte → Jacksonville*).

### 2. Interactive Map & Waypoints
- Free open-source routing using **Leaflet** with **OpenStreetMap** tiles.
- Exact highway routing geometry via **OSRM (Open Source Routing Machine)** with a mathematical **Great-Circle / Haversine fallback router**.
- Color-coded interactive map pins with detail popups:
  - 🟢 **Origin Departure**
  - 🔵 **Pickup Shipper** (1 hr on-duty)
  - 🔴 **Dropoff Consignee** (1 hr on-duty)
  - 🟡 **Fuel Stop** (at least once every 1,000 miles, 30 min on-duty)
  - ☕ **30-Minute Rest Break** (triggered after ≤ 8 hours of cumulative driving)
  - 🛏️ **10-Hour Mandatory Sleeper Berth / Reset** (triggered when 11h driving or 14h window is reached)

### 3. Official FMCSA Driver's Daily Log Sheets (24 Hours)
- **Authentic Paper Log Grid**: Exact reproduction of the FMCSA Form (24 hours: *Midnight* to *Midnight*).
- **4 Standard Duty Status Lines**:
  - `Line 1: Off Duty`
  - `Line 2: Sleeper Berth`
  - `Line 3: Driving`
  - `Line 4: On Duty (not driving)`
- **15-Minute Resolution**: Full hourly marks with 15-, 30-, and 45-minute sub-ticks.
- **Continuous Step Line**: Continuous SVG vector path showing exact duty status transitions.
- **Strict 24.0-Hour Invariant**: Every calendar day cleanly totals to **exactly 24.00 hours** across lines 1–4.
- **Multi-Day Pagination**: Seamless tab switcher for multi-day journeys (e.g., *Day 1 of 5*, *Day 2 of 5*).
- **Remarks Table**: City/state, timestamps, miles, and official duty status annotations.
- **70-Hour / 8-Day Recap Box**:
  - Line 3 + 4 today
  - Line A: Total hours on duty last 7 days including today
  - Line B: Total hours available tomorrow ($70 - A$)
  - Line C: Total hours on duty last 8 days including today
- **Print / PDF Ready**: Dedicated print stylesheet formatted for standard 8.5" × 11" logbook pages.

---

## ⚖️ HOS & Business Rules (FMCSA 49 CFR § 395)

The scheduling engine enforces the federal property-carrying rules without adverse conditions:

| Regulation | FMCSA Standard | Implementation in Spotter ELD |
| :--- | :--- | :--- |
| **11-Hour Driving Limit** | Max 11 driving hours per shift | Driving halts at 11.0h; triggers 10h consecutive sleeper berth |
| **14-Hour Duty Window** | Cannot drive past 14th consecutive hour of shift | Shift window includes inspections, driving, and breaks; triggers 10h rest |
| **30-Minute Rest Break** | Required after 8 cumulative hours of driving | Scheduled after ≤ 8h driving as 30m Off Duty or Sleeper Berth |
| **10-Hour Reset** | Required to reset 11h / 14h clocks | 10 consecutive hours Sleeper Berth scheduled at end of each shift |
| **70-Hour / 8-Day Rule** | Max 70 on-duty hours in 8 days | Tracks cumulative on-duty time + prior cycle; computes available tomorrow |
| **Fueling Rule** | At least once every 1,000 miles | Scheduled at 900–1,000 miles intervals; 30 min On-Duty Not Driving |
| **Pickup Stop** | Shipper loading | 1.0 hour On-Duty Not Driving |
| **Dropoff Stop** | Consignee unloading | 1.0 hour On-Duty Not Driving |
| **Pre-Trip Inspection** | Vehicle walkaround | 15 minutes On-Duty Not Driving at shift start |

---

## 🏛️ Architecture & System Design

The application follows **Clean Architecture** and **Domain-Driven Design (DDD)** principles with strict separation of concerns:

```
assessment-spotter/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── spotter_project/          # Django core (settings, WSGI, URLs)
│   ├── apps/
│   │   ├── common/               # Constants, exceptions, math utils, pagination
│   │   ├── routing/              # Routing Domain
│   │   │   ├── domain/           # Coordinates, Location, RouteLeg, RouteStop
│   │   │   └── services/         # GeocodingService, OSRMRoutingService, FallbackRouter
│   │   ├── hos/                  # Hours of Service (HOS) Engine
│   │   │   ├── domain/           # DutyStatus, LogSegment, DailyLogSheet, HOSRuleEngine
│   │   │   └── services/         # TripScheduler, RecapCalculator
│   │   └── trips/                # REST API Layer & Persistence
│   │       ├── models.py         # Trip persistence model
│   │       ├── serializers.py    # Request/Response validation
│   │       ├── views.py          # PlanTripAPIView, GeocodeSuggestAPIView, HealthAPIView
│   │       └── urls.py
│   └── tests/                    # Backend automated tests
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── src/
│       ├── api/                  # Axios HTTP client & Trips API methods
│       ├── components/
│       │   ├── Common/           # Navbar, Header, Status Badges
│       │   ├── TripForm/         # Input form, validation, presets
│       │   ├── Map/              # Leaflet map, custom pins, route polyline
│       │   ├── TripSummary/      # KPI metrics cards & cycle progress bar
│       │   ├── Timeline/         # Chronological stop & rest itinerary
│       │   └── EldLog/           # FMCSA 24h log grid canvas, remarks, recap
│       ├── theme/                # Custom Material UI enterprise theme
│       ├── types/                # Strongly-typed domain interfaces
│       ├── App.tsx               # Root state orchestrator
│       └── main.tsx
└── README.md
```

### Key Architectural Strengths:
1. **Zero Domain Logic in Views**: Django views merely serialize HTTP payloads and invoke the `TripScheduler` service.
2. **Zero Business Logic in React UI**: React components only receive typed properties and render UI; all calculations are executed deterministically on the backend.
3. **Resilient Geocoding & Routing**: Built-in freight hub coordinates dictionary + OpenStreetMap Nominatim + OSRM routing + Great-Circle fallback. The app never fails or crashes if an external map provider is temporarily unreachable.
4. **Pure 24-Hour Calendar Day Partitioning**: The scheduler slices continuous cross-midnight events (such as 10-hour overnight sleeps) exactly at midnight so every day sheet's 4 duty lines sum to 24.00 hours.

---

## 🛠️ Tech Stack

- **Backend**:
  - Python 3.13 / 3.11+
  - Django 5.1 & Django REST Framework (DRF)
  - SQLite (zero configuration, persistent trips storage)
  - `pytest` & `pytest-django`
  - `django-cors-headers`
  - `requests`
- **Frontend**:
  - React 19 & TypeScript
  - Material UI (MUI v6)
  - Leaflet & OpenStreetMap tiles
  - Emotion (`@emotion/react`, `@emotion/styled`)
  - Vite build tool
  - Axios

---

## 💻 Local Development & Setup

### Prerequisites
- Python 3.11+ (Python 3.13 supported)
- Node.js 18+ (Node 20/22/24 recommended)
- Git

### 1. Clone Repository & Setup Backend
```bash
# Navigate to the project root
cd /Users/paras/Desktop/CL/Assessment/assessment-spotter

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Run database migrations
python backend/manage.py migrate

# Run the Django REST API server on port 8008
python backend/manage.py runserver 127.0.0.1:8008
```
> The backend will be live at `http://127.0.0.1:8008/api/health/`.

### 2. Setup Frontend
In a new terminal:
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server
npm run dev -- --port 5173
```
> Open your browser at `http://127.0.0.1:5173`.

---

## 📡 API Specification

### 1. Health Check
- **Endpoint**: `GET /api/health/`
- **Response**:
```json
{
  "status": "healthy",
  "service": "Spotter ELD & HOS Trip Planner",
  "version": "1.0.0"
}
```

### 2. City Suggestion / Autocomplete
- **Endpoint**: `GET /api/trips/suggest/?q=chic`
- **Response**:
```json
[
  {
    "name": "Chicago, IL",
    "latitude": 41.8781,
    "longitude": -87.6298,
    "state": "IL"
  }
]
```

### 3. Plan Trip & Generate ELD Logs
- **Endpoint**: `POST /api/trips/plan/`
- **Request Body**:
```json
{
  "current_location": "Chicago, IL",
  "pickup_location": "Indianapolis, IN",
  "dropoff_location": "Dallas, TX",
  "current_cycle_used": 12.5
}
```
- **Response Structure (Status 201 Created)**:
```json
{
  "id": 1,
  "summary": {
    "origin": "Chicago, IL",
    "pickup": "Indianapolis, IN",
    "dropoff": "Dallas, TX",
    "total_distance_miles": 1080.3,
    "total_driving_hours": 19.64,
    "total_on_duty_hours": 22.39,
    "total_sleeper_hours": 10.0,
    "total_off_duty_hours": 15.61,
    "total_trip_days": 2,
    "fuel_stops_count": 1,
    "rest_stops_count": 3,
    "initial_cycle_used": 12.5,
    "final_cycle_used": 34.89,
    "cycle_hours_remaining": 35.11
  },
  "route": {
    "geojson": { "type": "LineString", "coordinates": [[-87.62, 41.87], ...] },
    "legs": [...]
  },
  "stops": [
    {
      "stop_type": "PICKUP",
      "name": "Shipper - Indianapolis, IN",
      "arrival_time": "2026-10-02T09:45:00",
      "departure_time": "2026-10-02T10:45:00",
      "duration_hours": 1.0,
      "cumulative_miles": 182.4,
      "remark": "1 Hour Loading & Paperwork (On-Duty Not Driving)"
    },
    ...
  ],
  "daily_logs": [
    {
      "date": "2026-10-02",
      "day_number": 1,
      "total_days": 2,
      "total_miles_driving_today": 605.0,
      "totals": {
        "off_duty": 6.5,
        "sleeper_berth": 5.25,
        "driving": 11.0,
        "on_duty_not_driving": 1.25,
        "total_hours": 24.0
      },
      "segments": [...],
      "recap": {
        "on_duty_today": 12.25,
        "hours_last_7_days_including_today": 24.75,
        "hours_available_tomorrow": 45.25,
        "hours_last_8_days_including_today": 24.75
      }
    }
  ]
}
```

---

## 🧪 Automated Testing Suite

The backend includes comprehensive test coverage for HOS shift limits, fuel frequencies, 24-hour day invariants, and REST API contracts.

Run the test suite using `pytest`:
```bash
./venv/bin/pytest
```

**Test Results**:
```
backend/tests/test_trips_api.py ....                 [ 36%]
backend/tests/test_hos_rules.py ....                 [ 72%]
backend/tests/test_trip_scheduler.py ...             [100%]
============================== 11 passed in 5.02s ==============================
```

Frontend production build check:
```bash
cd frontend && npm run build
```
*(Transpiles and bundles cleanly with 0 TypeScript errors).*

---

## 🌐 Live Deployment Guide

### Option 1: Frontend on Vercel
1. Set the Root Directory to `frontend`.
2. Framework Preset: **Vite**.
3. Build Command: `npm run build`.
4. Output Directory: `dist`.
5. Environment Variable:
   - `VITE_API_URL`: URL of your deployed Django backend (e.g. `https://spotter-backend.railway.app`).

### Option 2: Backend on Railway / Render
1. Railway detects `backend/requirements.txt` or a root `Dockerfile`.
2. Start Command:
   ```bash
   gunicorn spotter_project.wsgi:application --bind 0.0.0.0:$PORT
   ```
3. Environment Variables:
   - `DJANGO_SECRET_KEY`: Set secure random key.
   - `DJANGO_DEBUG`: `False`.
   - `ALLOWED_HOSTS`: `*` (or your domain).

---

## 🎥 3-5 Minute Loom Presentation Script

Use this structured script when recording your 3–5 minute Loom video walk-through:

### 1. Introduction (0:00 – 0:45)
- *"Hi everyone! In this video, I'm presenting the Full-Stack ELD & HOS Trip Planner application built with Django REST Framework and React with TypeScript and Material UI."*
- *"The objective of the system is to take commercial trip parameters—current location, pickup, dropoff, and current cycle hours used—and compute an optimal route, automatically schedule required FMCSA stops, and generate official 24-hour Driver's Daily Log sheets with step-line graph grids."*

### 2. Live Demo & Presets (0:45 – 2:00)
- *"Let's test the application. I've built quick evaluation presets right into the form."*
- *Click **'Chicago → Indy → Dallas'**: Show the KPI metrics updating (1,080 miles, 1 fuel stop, 3 rest stops, 2 daily log sheets).*
- *Point to the **Leaflet map**: Show the route polyline and distinct marker pins for Origin, Shipper pickup, Consignee dropoff, Fuel stops, and 10-hour sleeper resets.*
- *Point to the **Itinerary Timeline**: Show exact timestamps and duration for each activity.*

### 3. The 24-Hour FMCSA Daily Log Sheets (2:00 – 3:15)
- *Scroll down to the **Driver's Daily Log Sheet**:*
- *"Here is the official FMCSA Form. Notice how the SVG grid renders all 24 hours with 15-minute tick marks across the four standard lines: 1. Off Duty, 2. Sleeper Berth, 3. Driving, and 4. On Duty."*
- *"Notice the bold continuous step line tracking every duty change. On the right, every line has its exact calculated total, and the daily sum equals exactly 24.00 hours."*
- *Click on **'Day 2 of 2'**: Show how the overnight 10-hour sleeper berth was cleanly split across midnight without losing a single minute.*
- *Point out the **Remarks Table** and the **70-Hour / 8-Day Recap Box** ($70 - A$).*
- *Click the **'New York → Chicago → LA'** preset: Show 5 days of log sheets generated seamlessly with multiple fuel stops and sleeper berth periods.*

### 4. Architecture & Code Highlights (3:15 – 4:30)
- *Open the codebase and highlight:*
  - `apps/hos/services/trip_scheduler.py`: *The domain simulation engine enforcing 11h driving, 14h window, 30m break, and 1,000-mile fueling intervals.*
  - `apps/hos/domain/hos_rules.py`: *The HOS compliance validator.*
  - `frontend/src/components/EldLog/EldGridCanvas.tsx`: *The SVG canvas rendering the official 24-hour grid.*
  - `backend/tests/`: *The automated test suite with 11 passing unit and integration tests.*
- *"Thank you for your time and consideration!"*
