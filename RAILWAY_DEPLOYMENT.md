# 🚂 Railway Deployment Guide for City Governance System

## ✅ Files Created for Railway

The following files have been added to support Railway deployment:

1. **`railway.toml`** - Primary Railway configuration
2. **`railway.json`** - Alternative Railway config
3. **`nixpacks.toml`** - Nixpacks build configuration
4. **`Procfile`** - Process file for web service
5. **`start.sh`** - Startup script
6. **`runtime.txt`** - Python version specification
7. **`requirements.txt`** - Root-level dependencies (copy of backend/requirements.txt)
8. **`.env.railway.example`** - Example environment variables

## 🚀 Deployment Steps

### Step 1: Create Railway Project

1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose `varshneytarang/City-Governance-System`

### Step 2: Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway will automatically create a Postgres service
4. Note the connection details (or use Railway's internal networking)

### Step 3: Configure Backend Service

1. Your backend service should auto-deploy from GitHub
2. Go to **Settings** → **Environment Variables**
3. Add the following variables:

#### Required Environment Variables

```bash
# Database (use Railway's internal networking)
DB_HOST=${{Postgres.RAILWAY_PRIVATE_DOMAIN}}
DB_PORT=5432
DB_NAME=railway
DB_USER=postgres
DB_PASSWORD=${{Postgres.POSTGRES_PASSWORD}}

# LLM Configuration
GROQ_API_KEY=your-groq-api-key-here
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.3

# Application
ENVIRONMENT=production
PYTHONUNBUFFERED=1
```

**💡 Pro Tip:** Railway auto-sets the `PORT` variable, so don't set it manually.

### Step 4: Initialize Database Schema

After deployment, run this command in Railway's shell:

```bash
psql $DATABASE_URL -f migrations/complete_schema.sql
```

Or use Railway's database GUI to import the schema.

### Step 5: Verify Deployment

1. Check the deployment logs for any errors
2. Visit your app's health endpoint:
   ```
   https://<your-app-name>.railway.app/health
   ```
   Should return: `{"status":"ok"}`

3. Access API documentation:
   ```
   https://<your-app-name>.railway.app/docs
   ```

## 🔍 Troubleshooting

### Build Fails

**Error:** "Railpack could not determine how to build"
- **Fix:** Ensure `railway.toml`, `Procfile`, or `nixpacks.toml` exists in root

**Error:** "Module not found"
- **Fix:** Verify `requirements.txt` is in root directory
- **Fix:** Check `PYTHONPATH` environment variable is set

### Database Connection Issues

**Error:** "Connection refused"
- **Fix:** Use Railway's internal networking:
  ```
  DB_HOST=${{Postgres.RAILWAY_PRIVATE_DOMAIN}}
  ```
- **Fix:** Verify database service is running

**Error:** "Database does not exist"
- **Fix:** Initialize schema using Railway shell or pgAdmin

### Application Crashes

**Check logs:**
```bash
railway logs
```

**Common issues:**
- Missing environment variables (especially `GROQ_API_KEY`)
- Database schema not initialized
- Port binding (Railway sets `$PORT` automatically)

## 📊 Service Architecture

```
┌─────────────────┐      ┌──────────────────┐
│   PostgreSQL    │◄─────┤  Backend (API)   │
│   (Database)    │      │  Python/FastAPI  │
└─────────────────┘      └──────────────────┘
                                  │
                                  ▼
                         https://your-app.railway.app
```

## 🔗 Important URLs

Once deployed, you'll have access to:

- **API Base:** `https://<your-app>.railway.app`
- **Health Check:** `https://<your-app>.railway.app/health`
- **API Docs:** `https://<your-app>.railway.app/docs`
- **Query Endpoint:** `POST https://<your-app>.railway.app/api/v1/query`

## 🔒 Security Checklist

- [ ] Set strong `DB_PASSWORD` (use Railway's generated password)
- [ ] Keep `GROQ_API_KEY` secret (don't commit to git)
- [ ] Use Railway's private networking for database
- [ ] Enable CORS only for trusted domains (update `app/server.py`)
- [ ] Review Railway's security best practices

## 💰 Cost Optimization

- **Free Tier:** Railway offers $5 free credit/month
- **Database:** PostgreSQL usage counts toward quota
- **Optimization:** Use Railway's sleep/wake feature for dev environments

## 📝 Environment Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_HOST` | Yes | - | Database hostname (use Railway internal) |
| `DB_PORT` | Yes | 5432 | Database port |
| `DB_NAME` | Yes | railway | Database name |
| `DB_USER` | Yes | postgres | Database user |
| `DB_PASSWORD` | Yes | - | Database password |
| `GROQ_API_KEY` | Yes | - | Groq LLM API key |
| `LLM_PROVIDER` | No | groq | LLM provider (groq/openai) |
| `LLM_MODEL` | No | llama-3.3-70b-versatile | Model name |
| `PORT` | Auto | - | Railway sets automatically |

## 🔄 Continuous Deployment

Railway automatically deploys when you push to the `main` branch:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Railway will:
1. Detect the push
2. Build the new image
3. Run health checks
4. Deploy with zero downtime

## 📞 Support

- **Railway Docs:** https://docs.railway.app
- **Railway Discord:** https://discord.gg/railway
- **Project Issues:** https://github.com/varshneytarang/City-Governance-System/issues

---

**🎉 Your City Governance System is now ready for Railway deployment!**
