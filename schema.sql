-- Optional: run this manually if you prefer not to auto-create on startup
CREATE TABLE IF NOT EXISTS meals (
    id BIGSERIAL PRIMARY KEY,
    logged_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    food TEXT NOT NULL,
    calories REAL NOT NULL,
    protein REAL DEFAULT 0,
    carbs REAL DEFAULT 0,
    fat REAL DEFAULT 0,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_meals_logged_at ON meals(logged_at);
