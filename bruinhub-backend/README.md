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

## API Endpoints

### Gym Data
- `GET /api/v1/gym/<slug>` - Get latest data for a specific gym
  - BFIT: `/api/v1/gym/bfit`
  - Wooden Center: `/api/v1/gym/wooden`

### Health Check
- `GET /health` - Check service health and database connectivity 