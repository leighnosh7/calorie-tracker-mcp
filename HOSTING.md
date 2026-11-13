# Free hosting options for the Calorie Tracker MCP

The server now supports both **stdio** (local Cursor) and **Streamable HTTP** (remote).

## Recommended free stack

| Piece | Service | Free tier notes |
|-------|---------|-----------------|
| Postgres | **Neon** or **Supabase** | Generous free tier, no sleep |
| MCP server | **Render** or **Fly.io** | Free web service (may sleep on Render) |

## 1. Database (Neon – easiest)

1. Sign up at neon.tech
2. Create a project → copy the connection string  
   Example: `postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require`
3. That’s your `DATABASE_URL`

## 2. Host the MCP server (Render free tier)

1. Push this folder to a GitHub repo
2. Go to render.com → New → Web Service → connect the repo
3. Settings:
   - **Runtime**: Python
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**:  
     `MCP_TRANSPORT=streamable-http python server_postgres.py`
   - **Environment variables**:
     - `DATABASE_URL` = your Neon connection string
     - `MCP_TRANSPORT` = `streamable-http`
4. Deploy. You’ll get a URL like `https://calorie-tracker-mcp.onrender.com`

## 3. Connect from Cursor

In `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "calorie-tracker": {
      "url": "https://your-app.onrender.com/mcp",
      "transport": "streamable-http"
    }
  }
}
```

## Other free options

- **Fly.io** – better for always-on, free allowance
- **Koyeb** / **Railway** – limited free tiers
- **Oracle Cloud Always Free** – free VM if you want full control

## Notes

- Render free tier sleeps after ~15 min of inactivity (first request is slow).
- For always-on free, prefer Fly.io or a small Oracle Cloud VM.
- Never commit your `DATABASE_URL`.
