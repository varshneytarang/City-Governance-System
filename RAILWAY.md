# Railway Deployment Configuration

## Backend Service

### Environment Variables
Set these in Railway dashboard:

```
DB_HOST=<postgres-service-name>.railway.internal
DB_PORT=5432
DB_NAME=departments
DB_USER=postgres
DB_PASSWORD=<set-securely>
GROQ_API_KEY=<your-groq-key>
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.3
PORT=8000
```

### Deploy Steps
1. Create new Railway project
2. Add PostgreSQL database service
3. Add backend service from GitHub repo
4. Set environment variables above
5. Deploy

### Health Check
- Path: `/health`
- Should return: `{"status":"ok"}`

### Endpoints
- Backend: `https://<your-app>.railway.app`
- Health: `https://<your-app>.railway.app/health`
- API Docs: `https://<your-app>.railway.app/docs`
