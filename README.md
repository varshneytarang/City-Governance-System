# City Governance System 🏛️

A comprehensive multi-agent AI system for managing city department operations including Water, Fire, Engineering, Health, Finance, and Sanitation services.

## 🎯 Overview

The City Governance System uses LangGraph-based AI agents to automate and optimize city department workflows. Each department has a specialized agent that handles requests, coordinates with other departments, and maintains operational data.

### Key Features
- **Multi-Agent Architecture**: 7 specialized agents (1 coordination + 6 departments)
- **LLM Integration**: Powered by Groq/OpenAI for intelligent decision-making
- **Database-Driven**: PostgreSQL backend with 31 comprehensive tables
- **RESTful API**: FastAPI for high-performance backend services
- **Modern Frontend**: React + Vite with optimized video animations
- **Containerized Deployment**: Docker + Docker Compose for easy deployment

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Coordination Agent                         │
│              (Routes to Department Agents)                   │
└────────┬───────┬────────┬────────┬────────┬─────────────────┘
         │       │        │        │        │         │
    ┌────▼──┐ ┌─▼───┐ ┌──▼──┐ ┌───▼──┐ ┌───▼──┐ ┌───▼──────┐
    │ Water │ │Fire │ │Engi-│ │Health│ │Finan-│ │Sanitation│
    │ Agent │ │Agent│ │neeri│ │Agent │ │ce    │ │Agent     │
    │       │ │     │ │ng   │ │      │ │Agent │ │          │
    └───────┘ └─────┘ └─────┘ └──────┘ └──────┘ └──────────┘
         │       │        │        │        │         │
         └───────┴────────┴────────┴────────┴─────────┘
                            │
                    ┌───────▼────────┐
                    │   PostgreSQL   │
                    │   (31 Tables)  │
                    └────────────────┘
```

## 📁 Project Structure

```
City-Governance-System/
├── backend/                    # Backend API & AI agents
│   ├── agents/                # Multi-agent system
│   │   ├── coordination_agent/  # Main router agent
│   │   ├── water_agent/         # Water department
│   │   ├── fire_agent/          # Fire & emergency
│   │   ├── engineering_agent/   # Infrastructure
│   │   ├── health_agent/        # Public health
│   │   ├── finance_agent/       # Budget & finance
│   │   └── sanitation_agent/    # Waste management
│   ├── app/                   # FastAPI application
│   ├── migrations/            # Database schemas
│   ├── scripts/               # Utility scripts
│   ├── tests/                 # Test suite
│   ├── main.py                # Entry point
│   ├── global_config.py       # LLM configuration
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Backend container
├── frontend/                   # React frontend
│   ├── src/                   # React components
│   ├── public/                # Static assets
│   ├── nginx.conf             # Production server config
│   ├── package.json           # npm dependencies
│   └── Dockerfile             # Frontend container
├── migrations/                 # Shared database files
│   ├── complete_schema.sql    # Full database schema
│   └── comprehensive_seed_data.sql  # Sample data
├── docker-compose.yml          # Service orchestration
├── DEPLOYMENT.md              # Deployment guide
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites
- Docker 24.0+ and Docker Compose 2.20+
- API keys: Groq (recommended) or OpenAI

### Installation

1. **Clone Repository**
   ```bash
   git clone <your-repo-url>
   cd City-Governance-System
   ```

2. **Configure Environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit with your API keys
   notepad .env  # Windows
   ```

3. **Start Services**
   ```bash
   # Initialize database
   docker-compose up -d postgres
   
   # Wait 10 seconds for database to be ready
   
   # Start all services
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   ```

4. **Access Application**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🛠️ Development

### Backend Development
```bash
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
$env:GROQ_API_KEY="your_key"
$env:DATABASE_HOST="localhost"

# Run backend
python main.py
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

### Running Tests
```bash
# Using Docker
docker-compose exec backend pytest

# Local environment
cd backend
pytest

# Specific test file
pytest tests/test_health_agent.py

# With coverage
pytest --cov=agents --cov-report=html
```

## 🎭 Agent System

### Coordination Agent
- Routes requests to appropriate department agents
- Maintains conversation context
- Handles multi-department coordination

### Department Agents
Each agent follows a 6-node LangGraph workflow:
1. **Extract Info**: Parse user request
2. **Retrieve Context**: Fetch relevant database data
3. **Decide Action**: Determine next steps
4. **Execute Tools**: Run database operations
5. **LLM Reason**: Generate intelligent response
6. **Coordinate**: Handle cross-department needs

### Available Agents
- **Water Agent**: Reservoir management, consumption tracking, water quality
- **Fire Agent**: Emergency response, incident tracking, resource allocation
- **Engineering Agent**: Infrastructure projects, maintenance, permits
- **Health Agent**: Disease surveillance, facility management, public health
- **Finance Agent**: Budget tracking, grant management, financial reporting
- **Sanitation Agent**: Waste collection, recycling, street cleaning

## 📊 Database Schema

31 comprehensive tables across 6 departments:
- **Water**: 7 tables (reservoirs, pipelines, consumption, quality, maintenance)
- **Fire**: 5 tables (incidents, stations, vehicles, personnel, equipment)
- **Engineering**: 5 tables (projects, permits, infrastructure, contractors)
- **Health**: 7 tables (diseases, facilities, inspections, vaccinations)
- **Finance**: 4 tables (budgets, accounts, grants, reserves)
- **Sanitation**: 3 tables (routes, complaints, recycling)

### Sample Data
450+ realistic records including:
- $15M+ in tracked financial data
- 32 municipal workers
- 19 active projects
- 15 historical incidents
- 200+ water quality readings

## 🔧 Configuration

### LLM Providers
```python
# In global_config.py or .env
LLM_PROVIDER=groq  # or openai
LLM_MODEL=llama-3.1-70b-versatile

# API Keys
GROQ_API_KEY=gsk_...
OPENAI_API_KEY=sk-...
```

### Database Connection
```python
DATABASE_HOST=postgres  # or localhost
DATABASE_PORT=5432
DATABASE_NAME=departments
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
```

## 📦 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guide including:
- Docker production deployment
- Cloud deployment (AWS/GCP/Azure)
- Database backups and migrations
- Performance tuning
- Security checklist
- Monitoring and logging

### Quick Production Deploy
```bash
# Build production images
docker-compose build

# Start in production mode
ENVIRONMENT=production docker-compose up -d

# Scale backend
docker-compose up -d --scale backend=3
```

## 🎨 Frontend Features

### Video-Optimized Agent Constellation
Replaced heavy JavaScript animations with optimized video:
- **Performance**: 85% CPU reduction, 60% memory reduction
- **Quality**: 1080p 60fps smooth playback
- **Compatibility**: MP4 + WebM fallback
- **Mobile**: Responsive 720p 30fps version

See [frontend/VIDEO_IMPLEMENTATION_GUIDE.md](frontend/VIDEO_IMPLEMENTATION_GUIDE.md) for details.

## 📝 API Examples

### Query Water Agent
```bash
curl -X POST http://localhost:8000/api/agent/water \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the current water quality at Sterling Reservoir?"}'
```

### Get Department Status
```bash
curl http://localhost:8000/api/departments
```

### Health Check
```bash
curl http://localhost:8000/health
```

## 🧪 Testing

### Test Coverage
- Unit tests for each agent's nodes
- Integration tests for multi-agent workflows
- Database connectivity tests
- LLM integration tests (rate-limited)

### Run Tests
```bash
# All tests
pytest

# Specific agent
pytest tests/test_water_agent.py

# Skip slow tests
pytest -m "not slow"

# With output
pytest -v -s
```

## 🔒 security

- API keys managed via environment variables
- Database credentials in .env (never committed)
- Docker non-root user configuration
- Nginx security headers
- CORS configuration for API access
- Rate limiting on API endpoints
- SQL injection protection via parameterized queries

## 📈 Performance

### Backend
- Async FastAPI for concurrent requests
- Database connection pooling
- LLM response caching
- Efficient LangGraph state management

### Frontend
- Code splitting and lazy loading
- Video compression (H.264/VP9)
- Static asset caching
- Nginx gzip compression

### Database
- Indexed foreign keys
- Query optimization
- Connection pooling
- Regular VACUUM and ANALYZE

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React
- Write tests for new features
- Update documentation
- Keep commits atomic and descriptive

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**Backend won't start**
```bash
# Check logs
docker-compose logs backend

# Verify API keys
docker-compose exec backend env | grep API_KEY
```

**Database connection failed**
```bash
# Check database is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres pg_isready
```

**Import errors**
```bash
# Verify PYTHONPATH
docker-compose exec backend env | grep PYTHONPATH

# Should show: PYTHONPATH=/app
```

See [DEPLOYMENT.md#troubleshooting](DEPLOYMENT.md#troubleshooting) for complete troubleshooting guide.

## 📚 Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) - Complete deployment guide
- [frontend/VIDEO_IMPLEMENTATION_GUIDE.md](frontend/VIDEO_IMPLEMENTATION_GUIDE.md) - Video optimization
- [frontend/VIDEO_GENERATION_PROMPT.md](frontend/VIDEO_GENERATION_PROMPT.md) - AI video generation
- [PHASE3_FEATURES_COMPLETE.md](PHASE3_FEATURES_COMPLETE.md) - Feature documentation
- [PHASE4_POLISH_COMPLETE.md](PHASE4_POLISH_COMPLETE.md) - Polish and refinements

## 🎯 Roadmap

- [ ] Real-time WebSocket notifications
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Kubernetes deployment configurations
- [ ] Multi-tenant support
- [ ] Advanced caching layer (Redis)
- [ ] Automated testing pipeline

## 📞 Support

For issues, questions, or contributions:
1. Check existing documentation
2. Review troubleshooting guide
3. Open an issue on GitHub
4. Provide logs and environment details

---

**Built with ❤️ using FastAPI, LangGraph, React, and Docker**
