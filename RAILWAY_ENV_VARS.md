# Railway Environment Variables - Correct Configuration

## ✅ Required Variables (Set These in Railway Dashboard)

### Database Configuration
Use Railway's variable references (these will auto-populate):

```
DB_HOST = ${{Postgres.RAILWAY_PRIVATE_DOMAIN}}
DB_PORT = 5432
DB_NAME = railway
DB_USER = postgres
DB_PASSWORD = ${{Postgres.POSTGRES_PASSWORD}}
```

**Note:** Railway will automatically expand `${{...}}` syntax when you use their UI. Don't put quotes around these references!

### LLM Configuration
**⚠️ CRITICAL:** Replace with your actual Groq API key!

```
GROQ_API_KEY = gsk_your_actual_groq_api_key_here
LLM_PROVIDER = groq
LLM_MODEL = llama-3.3-70b-versatile
LLM_TEMPERATURE = 0.3
```

### Application Settings
```
ENVIRONMENT = production
LOG_LEVEL = INFO
MAX_PLANNING_ATTEMPTS = 3
CONFIDENCE_THRESHOLD = 0.7
```

## ❌ Remove These Variables

These are duplicates and conflicting with the main DB config:

```
# DELETE THESE:
HEALTH_DB_HOST
HEALTH_DB_NAME
HEALTH_DB_PASSWORD
HEALTH_DB_PORT
HEALTH_DB_USER
HEALTH_CONFIDENCE_THRESHOLD
```

The health agent should use the same database as configured in `DB_*` variables.

## 🚫 DO NOT SET

Railway automatically sets these:

```
# Railway auto-sets:
PORT (automatically assigned by Railway)
```

## How to Set Variables in Railway:

1. Go to your Railway project
2. Click on your backend service
3. Go to **Variables** tab
4. Click **+ New Variable**
5. For Postgres references:
   - Click **Variable Reference**
   - Select `Postgres` service
   - Select the field (e.g., `RAILWAY_PRIVATE_DOMAIN`, `POSTGRES_PASSWORD`)

## Quick Fix Checklist:

- [ ] Remove `HEALTH_DB_*` variables (use main `DB_*` instead)
- [ ] Set real `GROQ_API_KEY` (get from https://console.groq.com)
- [ ] Use Railway's variable reference UI for `DB_HOST` and `DB_PASSWORD`
- [ ] Do NOT set `PORT` variable manually
- [ ] Redeploy after fixing variables

## After Fixing:

Your final variables should look like:

```json
{
  "DB_HOST": "${{Postgres.RAILWAY_PRIVATE_DOMAIN}}",
  "DB_PORT": "5432",
  "DB_NAME": "railway",
  "DB_USER": "postgres",
  "DB_PASSWORD": "${{Postgres.POSTGRES_PASSWORD}}",
  "GROQ_API_KEY": "gsk_abc123...",
  "LLM_PROVIDER": "groq",
  "LLM_MODEL": "llama-3.3-70b-versatile",
  "LLM_TEMPERATURE": "0.3",
  "ENVIRONMENT": "production",
  "LOG_LEVEL": "INFO",
  "MAX_PLANNING_ATTEMPTS": "3",
  "CONFIDENCE_THRESHOLD": "0.7"
}
```

**Note:** Railway will display the references as the literal variable names in the UI, but they'll be properly expanded at runtime.
