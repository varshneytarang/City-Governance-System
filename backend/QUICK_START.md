# 🚀 Quick Start Guide - Fire Agent

## Immediate Action Required

### ⚠️ Set OpenAI API Key

Edit `backend/.env` and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

---

## Run Fire Agent Tests

```bash
cd backend
.\venv\Scripts\Activate.ps1
python test_fire_agent.py
```

Expected output: 4 emergency scenarios with dispatch plans, severity scores, coordination messages.

---

## Start API Server

```bash
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

Server will run at: **http://localhost:8000**

---

## Test API Endpoints

### Fire Emergency
```bash
curl -X POST http://localhost:8000/api/fire/emergency ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":1,\"location\":{\"latitude\":28.6139,\"longitude\":77.2090,\"address\":\"Connaught Place\"},\"description\":\"Building fire\",\"emergency_type\":\"fire\",\"priority\":\"critical\",\"casualties\":2,\"building_type\":\"commercial\",\"fire_intensity\":\"major\"}"
```

### Get Fire Stations
```bash
curl http://localhost:8000/api/fire/stations
```

### Get Active Incidents
```bash
curl http://localhost:8000/api/fire/incidents/active
```

---

## API Documentation

Once server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Next Steps

After testing Fire Agent, choose one:

### A) Build Inter-Agent Messaging 🤝
Create message bus for Water ↔ Fire coordination
- Implement message polling
- Create coordination workflows
- Test cross-department scenarios

### B) Build Frontend Dashboard 🖥️
Create UI for request submission
- React/Vue dashboard
- Real-time incident map
- Agent status monitoring

### C) Add More Agents 🚓
Health, Police, Public Works
- Follow same LangGraph pattern
- Add coordination logic
- Expand messaging system

---

## Troubleshooting

**Error: "OPENAI_API_KEY not set"**
→ Add API key to `.env` file

**Error: "Database connection failed"**
→ Check PostgreSQL is running
→ Verify credentials in `.env`

**Error: "Module not found"**
→ Ensure virtual environment is activated
→ Run `pip install -r requirements.txt`

**Slow LLM responses**
→ Normal for GPT-4 (5-15 seconds)
→ Can switch to GPT-3.5 for faster testing

---

## What's Working

✅ Water Agent (fully tested)  
✅ Fire Agent (code complete, needs API key)  
✅ Database (13 tables operational)  
✅ API Server (9 endpoints)  
✅ LangGraph workflows (both agents)  

## What's Next

⏳ Test Fire Agent  
⏳ Inter-agent messaging  
⏳ Frontend dashboard  
⏳ Additional agents  

---

**Ready to test?** Set your OpenAI API key and run the Fire Agent tests! 🚒
