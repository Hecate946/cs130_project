# BruinHub Backend

A Flask-based backend service that periodically scrapes UCLA facility data and stores it in a database. When the frontend requests facility information, it returns the most recent snapshot from the database rather than scraping on-demand. This approach reduces load on UCLA's servers and provides faster response times.

## Project Structure

### `/database`
Contains database interaction logic, separated by data domain:
- `manager.py` - Core database connection and management
- `gyms.py` - Gym-specific database operations (queries, snapshots, etc.)

Each domain file (like `gyms.py`) contains a class that handles all database operations for that specific type of data.

### `/migrations`
SQL migration files that define the database schema. These migrations are run on the GCP PostgreSQL instance, not locally.
- `create_gyms_and_snapshots.sql` - Creates tables for gyms and their snapshots

### `/models`
Data models that define the structure of our application's objects:
- `gyms.py` - Contains dataclasses for Gym, GymZoneSnapshot, and GymHoursSnapshot
- Additional model files can be added for new data domains

Models are used to ensure type safety and provide a clear interface for data structures throughout the application.

### `/scrapers`
Contains scraping logic for different data sources:
- `gyms.py` - Scraping logic for gym facilities (BFIT, Wooden Center)

Each scraper is responsible for converting web data into our application's data format. Currently using dummy data for testing, but will be replaced with actual web scraping logic.

### `/tasks`
Background task definitions and scheduling:
- `scheduler.py` - Configures and initializes periodic tasks
- `gym_tasks.py` - Defines gym-specific periodic tasks (e.g., scraping gym data)

Tasks are run on a schedule to keep our database updated with the latest facility information.

## Testing Scenarios

### API Tests

1. Retrieving a specific gym.

Success: The API returns the latest data for the specified gym.
Failure: The API returns an error or incorrect data.

2. Retrieving a nonexistent gym.

Success: The API returns a 404 error for a nonexistent gym.
Failure: The API returns a different status code or incorrect data.

3. Retrieving a specific dining hall.

Success: The API returns the latest data for the specified dining hall.
Failure: The API returns an error or incorrect data.

4. Retrieving a nonexistent dining hall.

Success: The API returns a 404 error for a nonexistent dining hall.
Failure: The API returns a different status code or incorrect data.

### Library Scraping Tests

1. Model creating a library reservation room and booking in the database.

Success: The library reservation room and booking are created in the database.
Failure: The library reservation room and booking are not created in the database.

2. Booking time constraints.

Success: Database returns error for start time after end time.
Failure: Database does not return error for start time after end time.

### Restaurant Scraping Tests

1. The shape of the Occuspace API and UCLA menus endpoints should not change.

Success: The Occuspace API and UCLA menus endpoints maintain the same structure.
Failure: The Occuspace API and UCLA menus endpoints change their structure.

### Gym Scraping Tests

1. Each facility's live counts are retrievable.

Success: The live counts for each facility are retrievable.
Failure: One or many facilities do not have retrievable live counts.

2. Zone data can be filtered correctly.

Success: The zone data can be filtered correctly.
Failure: The zone data cannot be filtered correctly, such as returning zones from the wrong facility or none at all.

## API Endpoints

### Gym Data
- `GET /api/v1/gym/<slug>` - Get latest data for a specific gym
  - BFIT: `/api/v1/gym/bfit`
  - Wooden Center: `/api/v1/gym/wooden`

### Health Check
- `GET /health` - Check service health and database connectivity
