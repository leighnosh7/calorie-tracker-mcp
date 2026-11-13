"""
Calorie Tracker MCP Server (Postgres)
Same tools as the SQLite version. Point it at any Postgres / Supabase database.
"""

import os
from datetime import datetime, date
from mcp.server import MCPServer
import psycopg

# ---------------------------------------------------------------------------
# Database
# Set DATABASE_URL in the environment (or in Cursor's MCP config).
# Example: postgresql://user:pass@localhost:5432/calories
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")

def get_conn():
    return psycopg.connect(DATABASE_URL)

def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS meals (
                    id BIGSERIAL PRIMARY KEY,
                    logged_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    food TEXT NOT NULL,
                    calories REAL NOT NULL,
                    protein REAL DEFAULT 0,
                    carbs REAL DEFAULT 0,
                    fat REAL DEFAULT 0,
                    notes TEXT
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_meals_logged_at ON meals(logged_at)
            """)
        conn.commit()

init_db()

# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
mcp = MCPServer(
    "calorie-tracker",
    instructions="Track meals and view daily macro totals. Data is stored in Postgres."
)

@mcp.tool()
def log_meal(
    food: str,
    calories: float,
    protein: float = 0,
    carbs: float = 0,
    fat: float = 0,
    notes: str = "",
    day: str | None = None,
) -> str:
    """Log a meal. Date defaults to today (YYYY-MM-DD)."""
    if day is None:
        day = date.today().isoformat()
    # Store at noon UTC on that day so the date is unambiguous
    logged_at = f"{day} 12:00:00+00"

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO meals (logged_at, food, calories, protein, carbs, fat, notes)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (logged_at, food, calories, protein, carbs, fat, notes or None),
            )
        conn.commit()

    return f"Logged: {food} — {calories} kcal, {protein}g P, {carbs}g C, {fat}g F on {day}"

@mcp.tool()
def get_daily_totals(day: str | None = None) -> dict:
    """Get total calories and macros for a day. Defaults to today."""
    if day is None:
        day = date.today().isoformat()

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT
                       COALESCE(SUM(calories), 0) as calories,
                       COALESCE(SUM(protein), 0) as protein,
                       COALESCE(SUM(carbs), 0) as carbs,
                       COALESCE(SUM(fat), 0) as fat,
                       COUNT(*) as meals
                   FROM meals
                   WHERE logged_at::date = %s""",
                (day,),
            )
            row = cur.fetchone()

    return {
        "date": day,
        "calories": round(float(row[0]), 1),
        "protein": round(float(row[1]), 1),
        "carbs": round(float(row[2]), 1),
        "fat": round(float(row[3]), 1),
        "meal_count": row[4],
    }

@mcp.tool()
def list_recent_meals(limit: int = 10, day: str | None = None) -> list[dict]:
    """List recent meals, optionally filtered by day."""
    query = """
        SELECT id, logged_at, food, calories, protein, carbs, fat, notes
        FROM meals
    """
    params = []
    if day:
        query += " WHERE logged_at::date = %s"
        params.append(day)
    query += " ORDER BY logged_at DESC LIMIT %s"
    params.append(limit)

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

    return [
        {
            "id": r[0],
            "logged_at": r[1].isoformat() if r[1] else None,
            "food": r[2],
            "calories": r[3],
            "protein": r[4],
            "carbs": r[5],
            "fat": r[6],
            "notes": r[7],
        }
        for r in rows
    ]

if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        mcp.run(transport="streamable-http", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
    else:
        mcp.run()  # stdio for local Cursor
