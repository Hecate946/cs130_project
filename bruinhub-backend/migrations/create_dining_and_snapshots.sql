BEGIN;

-- Create the dining_halls table
CREATE TABLE dining_halls (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    capacity INT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the dining_menu_snapshot table to store complete snapshots of dining menus
CREATE TABLE dining_menu_snapshot (
    id SERIAL PRIMARY KEY,
    hall_id INT REFERENCES dining_halls(id) ON DELETE CASCADE,
    snapshot_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    menu JSONB NOT NULL
    -- Expected JSON structure:
    --   {"Capri": ["Spinach Tortellini", "Shrimp Alfredo Pasta"],
    --    "Psistaria": ["Vegetarian Meatball Sandwich"],
    --    "Mezze": ["Roasted Carrots"]}
);

-- Create the dining_hours_snapshot table to store snapshots of dining hall hours
CREATE TABLE dining_hours_snapshot (
    id SERIAL PRIMARY KEY,
    hall_id INT REFERENCES dining_halls(id) ON DELETE CASCADE,
    snapshot_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    regular_hours JSONB,
    special_hours JSONB
    -- Expected JSON structure:
    --   regular_hours: {"Monday": "7:00-10:00", "Tuesday": "7:00-10:00", ...}
    --   special_hours: {"2025-01-26": "1:00-11:00", "2025-02-15": "closed", ...}
);

-- Insert initial dining hall entries
INSERT INTO dining_halls (name, capacity) VALUES 
    ('Epicuria', 100),
    ('De Neve', 20),
    ('Bruin Plate', 70)
ON CONFLICT (name) DO NOTHING;

COMMIT;
