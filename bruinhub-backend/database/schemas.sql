-- Create the dining_halls table (stores latest menu and hours)
CREATE TABLE IF NOT EXISTS dining_halls (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE,
    capacity INT NOT NULL,
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
    name VARCHAR(100) UNIQUE NOT NULL,
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
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

