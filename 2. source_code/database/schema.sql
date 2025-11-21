-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    health_goals JSONB,
    dietary_restrictions JSONB,
    budget_range VARCHAR(50),
    preferences JSONB,
    family_size INTEGER DEFAULT 1,
    profile_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recipes table
CREATE TABLE recipes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    ingredients JSONB NOT NULL,
    preparation_steps JSONB,
    nutrition_facts JSONB,
    meal_type VARCHAR(50), -- breakfast, lunch, dinner
    cultural_tags JSONB, -- Zambian, Traditional, Modern, etc.
    cost_per_serving DECIMAL(10,2),
    preparation_time INTEGER, -- in minutes
    difficulty_level VARCHAR(20),
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Meal plans table
CREATE TABLE meal_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    week_plan JSONB NOT NULL,
    shopping_list JSONB,
    total_estimated_cost DECIMAL(10,2),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vendors table
CREATE TABLE vendors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100), -- supermarket, local_market, farm
    location GEOGRAPHY(POINT, 4326),
    address TEXT,
    contact_phone VARCHAR(20),
    products JSONB, -- Available products
    rating DECIMAL(3,2),
    business_hours JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User progress table
CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    date DATE DEFAULT CURRENT_DATE,
    weight DECIMAL(5,2),
    meals_logged JSONB,
    water_intake INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_meal_plans_user_id ON meal_plans(user_id);
CREATE INDEX idx_vendors_location ON vendors USING GIST(location);
CREATE INDEX idx_user_progress_user_date ON user_progress(user_id, date);
-- ENHANCEMENT: Index for efficient filtering of recipes by type
CREATE INDEX idx_recipes_meal_type ON recipes(meal_type);