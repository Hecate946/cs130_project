# BruinHub Backend

A Flask-based backend service that periodically scrapes UCLA facility data and stores it in a database. When the frontend requests facility information, it returns the most recent snapshot from the database rather than scraping on-demand. This approach reduces load on UCLA's servers and provides faster response times.

## Project Structure

### Core Files
- `app.py` - Main Flask application entry point with core configuration and health check endpoint
- `scraper.py` - Standalone service that runs periodic data collection tasks
- `notifications_server.py` - Separate service for handling push notifications
- `requirements.txt` - Python package dependencies

### `/database`
Contains database interaction logic, separated by data domain:
- `db.py` - Core database connection and SQLAlchemy setup
- `gyms.py` - Gym-specific database operations (queries, snapshots)
- `dining.py` - Dining hall database operations
- `library.py` - Library database operations
- `rec.py` - Recreation center database operations

Each domain file contains a class that handles all database operations for that specific type of data.

### `/models`
Data models that define the structure of our application's objects:
- `gyms.py` - Models for Gym, GymZoneSnapshot, GymHoursSnapshot
- `dining.py` - Models for DiningHall and related entities
- `library.py` - Models for Library, Room, and Booking
- `notifications.py` - Models for DeviceToken and notification preferences

### `/routes`
API endpoint definitions and request handlers:
- `gyms.py` - Gym facility endpoints
- `dining.py` - Dining hall endpoints
- `library.py` - Library and room booking endpoints
- `historical.py` - Historical data endpoints
- `notifications.py` - Push notification endpoints

### `/scrapers`
Contains scraping logic for different data sources:
- `gyms.py` - Gym facilities (BFIT, Wooden Center)
- `dining.py` - Dining halls and menus
- `library.py` - Library room availability

### `/tasks`
Background task definitions and scheduling:
- `scheduler.py` - Task scheduler configuration
- `gym_tasks.py` - Periodic gym data collection
- `dining_tasks.py` - Periodic dining hall updates
- `library_tasks.py` - Library availability updates
- `rec_tasks.py` - Recreation center session management

### `/config`
Configuration files and constants:
- `base.py` - Core configuration (database URLs, etc.)
- `gyms.py` - Gym-specific constants and IDs
- `dining.py` - Dining facility IDs and endpoints
- `library.py` - Library system configuration

### `/services`
Business logic and utility services:
- `notification_service.py` - Push notification handling
- `notification_scheduler.py` - Scheduled notification checks

### `/tests`
Comprehensive test suite covering:
- API endpoints (`test_api.py`)
- Database operations (`test_*_database.py`)
- Scrapers (`test_*_scrapers.py`)
- Task scheduling (`test_task_scheduler.py`)
- Notifications (`test_notifications.py`)

## API Endpoints

### Health Check
- `GET /health` - Check service health and database connectivity

### Gym Data
- `GET /api/v1/gym` - List all gyms with current status
- `GET /api/v1/gym/<slug>` - Get latest data for a specific gym
  - Example: `/api/v1/gym/bfit`, `/api/v1/gym/john-wooden-center`

### Dining Data
- `GET /api/v1/dining` - List all dining halls with current status
- `GET /api/v1/dining/<slug>` - Get data for a specific dining hall
  - Example: `/api/v1/dining/epicuria-covel`

### Library Data
- `GET /api/v1/library` - List all libraries
- `GET /api/v1/library/<slug>` - Get details for a specific library
- `GET /api/v1/library/<slug>/rooms` - Get rooms for a specific library
- `GET /api/v1/library/<slug>/bookings` - Get current bookings
- `GET /api/v1/library/<slug>/bookings/range` - Get bookings for a date range
  - Required params: `start` and `end` (ISO 8601 format)
  - Example: `/api/v1/library/powell/bookings/range?start=2025-03-08T00:00:00&end=2025-03-08T23:59:59`

### Historical Data
- `GET /api/v1/historical/dining/<slug>` - Get historical capacity for a dining hall
- `GET /api/v1/historical/gym/<slug>` - Get historical capacity for a gym

### Notifications
- `POST /api/v1/notifications/register` - Register a device for push notifications
- `POST /api/notifications/check-now` - Manually trigger notification checks
- `POST /api/notifications/send-test` - Send a test notification

## Running the Services

```sh
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 3. Start the main API server
python app.py

# 4. Start the scraping service (in a separate terminal)
python scraper.py

# 5. Start the notifications service (in a separate terminal)
python notifications_server.py
```

## Testing

Run the test suite:
```sh
pytest
```

The tests cover:
- API endpoint functionality
- Database operations
- Data scraping logic
- Task scheduling
- Notification handling
- Error cases and edge conditions
