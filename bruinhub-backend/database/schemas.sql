-- Create the dining_halls table (stores latest menu and hours)
CREATE TABLE IF NOT EXISTS dining_halls (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL, -- e.g., "bplate", "deneve"
    menu JSONB DEFAULT '{}'::JSONB,   -- Station -> List of items
    hours_today JSONB DEFAULT '{}'::JSONB, -- Stores today's hours
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Capacity history table (tracks historical occupancy and capacity changes)
CREATE TABLE IF NOT EXISTS dining_capacity_history (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) REFERENCES dining_halls(slug) ON DELETE CASCADE, -- Foreign key using slug
    occupants INT NOT NULL,
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
    location VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the library_rooms table (stores individual rooms & capacity)
CREATE TABLE IF NOT EXISTS library_rooms (
    id SERIAL PRIMARY KEY,
    library_id INT REFERENCES libraries(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    capacity INT,
    accessibility_features TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (room_id, start_time, end_time)
);


-- Ensure initial dining halls exist
INSERT INTO dining_halls (slug, menu, hours_today)
VALUES 
    ('epicuria', '{}'::jsonb, '{}'::jsonb),
    ('deneve', '{}'::jsonb, '{}'::jsonb),
    ('bplate', '{}'::jsonb, '{}'::jsonb)
ON CONFLICT (slug) DO NOTHING;

-- Insert initial capacity history
INSERT INTO dining_capacity_history (slug, occupants, capacity, last_updated)
VALUES
    ('epicuria', 0, 0, NOW()),
    ('deneve', 0, 0, NOW()),
    ('bplate', 0, 0, NOW())
ON CONFLICT DO NOTHING;

-- Ensure initial gyms exist
INSERT INTO gyms (slug, regular_hours, special_hours)
VALUES 
    ('bfit', '{}'::jsonb, '{}'::jsonb),
    ('john-wooden-center', '{}'::jsonb, '{}'::jsonb)
ON CONFLICT (slug) DO NOTHING;
