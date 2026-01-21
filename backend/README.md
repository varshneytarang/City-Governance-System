# Backend Development

## Setup Virtual Environment

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux
```bash
python -m venv venv
source venv/bin/activate
```

## Install Dependencies
```bash
pip install -r requirements.txt
```

## Environment Setup
1. Copy `.env.example` to `.env`
2. Add your OpenAI API key to `.env`
3. Configure other settings as needed

## Run Development Server
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Access API at: http://localhost:8000
API Docs: http://localhost:8000/docs

## Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py              # Application settings
│   ├── governance_graph.py    # LangGraph workflow
│   └── routes/
│       └── governance.py      # API routes
├── main.py                    # FastAPI application
└── requirements.txt           # Python dependencies
```

## LangGraph Workflow

The governance workflow is defined in `app/governance_graph.py` and includes:
- Request analysis node
- Processing node
- Conditional routing

Test the workflow:
```bash
python app/governance_graph.py
```

## API Endpoints

- `GET /` - API info
- `GET /api/health` - Health check
- `GET /api/stats` - City statistics
- `POST /api/governance/process` - Process governance request
- `GET /api/governance/workflow/status` - Workflow status

## Tech Stack
- FastAPI - Web framework
- LangGraph - AI workflow orchestration
- LangChain - LLM integration
- Uvicorn - ASGI server
- SQLAlchemy - Database ORM
- Pydantic - Data validation
