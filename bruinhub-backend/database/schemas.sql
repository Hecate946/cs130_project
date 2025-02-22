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


-- Create the libraries table (stores library metadata)
CREATE TABLE IF NOT EXISTS libraries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE,
    slug VARCHAR(50) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location VARCHAR(200)
);

-- Create the library_rooms table (stores individual rooms & capacity)
CREATE TABLE IF NOT EXISTS library_rooms (
    id SERIAL PRIMARY KEY,
    library_id INT REFERENCES libraries(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    capacity INT,
    accessibility_features TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (library_id, name)
);

-- Create the library_bookings table (stores individual bookings associated with a library room)
CREATE TABLE IF NOT EXISTS library_bookings (
    id SERIAL PRIMARY KEY,
    room_id INT REFERENCES library_rooms(id) ON DELETE CASCADE,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status VARCHAR(20) CHECK (status IN ('available', 'booked')) NOT NULL DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (room_id, start_time, end_time)
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
