-- Create the dining_halls table (stores latest menu and hours)
CREATE TABLE IF NOT EXISTS dining_halls (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) UNIQUE,
    menu JSONB DEFAULT '{}'::JSONB,  -- Stores the latest menu (station -> list of items)
    regular_hours JSONB DEFAULT '{}'::JSONB, -- Stores regular hours
    special_hours JSONB DEFAULT '{}'::JSONB, -- Stores special hours
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Capacity history table (tracks historical capacity changes)
CREATE TABLE IF NOT EXISTS dining_capacity_history (
    id SERIAL PRIMARY KEY,
    hall_id INT REFERENCES dining_halls(id) ON DELETE CASCADE,
    capacity INT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the gyms table (stores gym metadata)
CREATE TABLE IF NOT EXISTS gyms (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) UNIQUE,
    regular_hours JSONB DEFAULT '{}'::JSONB, -- Stores regular hours
    special_hours JSONB DEFAULT '{}'::JSONB, -- Stores special hours
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the gym_zones table (stores individual zones & capacity)
CREATE TABLE IF NOT EXISTS gym_capacity_history (
    id SERIAL PRIMARY KEY,
    gym_id INT REFERENCES gyms(id) ON DELETE CASCADE,
    zone_name VARCHAR(100) NOT NULL,
    capacity INT NOT NULL,
    percentage INT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (gym_id, zone_name, capacity, percentage, last_updated)
);

-- Ensure initial dining halls exist
INSERT INTO dining_halls (slug, menu, regular_hours, special_hours)
VALUES 
    ('epicuria', '{}'::jsonb, '{}'::jsonb, '{}'::jsonb),
    ('de-neve', '{}'::jsonb, '{}'::jsonb, '{}'::jsonb),
    ('bruin-plate', '{}'::jsonb, '{}'::jsonb, '{}'::jsonb)
ON CONFLICT (slug) DO NOTHING;

-- Insert initial capacity history
INSERT INTO dining_capacity_history (hall_id, capacity, last_updated)
SELECT id, capacity, NOW()
FROM (
    VALUES
        ('epicuria', 100),
        ('de-neve', 20),
        ('bruin-plate', 70)
) AS t(slug, capacity)
JOIN dining_halls ON dining_halls.slug = t.slug;

-- Ensure initial gyms exist
INSERT INTO gyms (slug, regular_hours, special_hours)
VALUES 
    ('bfit', '{}'::jsonb, '{}'::jsonb),
    ('john-wooden-center', '{}'::jsonb, '{}'::jsonb)
ON CONFLICT (slug) DO NOTHING;
