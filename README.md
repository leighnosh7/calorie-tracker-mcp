# Calorie Tracker MCP (Postgres)

Minimal MCP server for logging meals and viewing daily totals.

- **Local**: stdio (Cursor)
- **Remote**: Streamable HTTP (Render / Fly.io / etc.)

## Tools

- `log_meal(food, calories, protein=0, carbs=0, fat=0, notes="", day=None)`
- `get_daily_totals(day=None)`
- `list_recent_meals(limit=10, day=None)`

## Quick start (local)

```bash
uv run --with "mcp[cli]" --with psycopg python server_postgres.py
```

Set `DATABASE_URL` first.

## Deploy

See [HOSTING.md](HOSTING.md) for free Render / Fly.io instructions.

### Render
Connect this repo. It uses `render.yaml`. Add `DATABASE_URL` in the dashboard.

### Fly.io
```bash
fly launch --copy-config
fly secrets set DATABASE_URL="postgresql://..."
fly deploy
```
