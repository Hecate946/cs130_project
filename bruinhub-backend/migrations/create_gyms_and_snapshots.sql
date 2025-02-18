BEGIN;

-- Create the gyms table
CREATE TABLE gyms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the gym_zones_snapshot table to store complete snapshots of gym zones
CREATE TABLE gym_zones_snapshot (
    id SERIAL PRIMARY KEY,
    gym_id INT REFERENCES gyms(id) ON DELETE CASCADE,
    snapshot_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    zones JSONB NOT NULL 
    -- Expected JSON structure: 
    --   [{"zone_name": "Cardio Zone", "open": true, "last_count": 58, "percentage": 97}, ...]
);

-- Create the gym_hours_snapshot table to store snapshots of gym hours
CREATE TABLE gym_hours_snapshot (
    id SERIAL PRIMARY KEY,
    gym_id INT REFERENCES gyms(id) ON DELETE CASCADE,
    snapshot_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    regular_hours JSONB,
    special_hours JSONB
    -- Expected JSON structure:
    --   regular_hours: {"Monday": "6:00-1:00", "Tuesday": "6:00-1:00", ...}
    --   special_hours: {"2025-01-26": "1:00-11:00", "2025-02-15": "closed", ...}
);

-- Insert initial gym entries
INSERT INTO gyms (name, slug) VALUES 
    ('BFIT', 'bfit'),
    ('John Wooden Center', 'john-wooden-center')
ON CONFLICT (slug) DO NOTHING;

COMMIT;
