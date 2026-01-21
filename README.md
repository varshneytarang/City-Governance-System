# City Governance System

A comprehensive city governance management system built with modern web technologies.

## Tech Stack

### Frontend
- **React** - UI library
- **Tailwind CSS** - Utility-first CSS framework
- **Vite** - Build tool and dev server

### Backend
- **Python** - Core backend language
- **LangGraph** - AI workflow orchestration
- **FastAPI** - Web framework (recommended)

## Project Structure

```
City-Governance-System/
├── frontend/           # React + Tailwind frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── backend/            # Python + LangGraph backend
│   ├── app/
│   ├── requirements.txt
│   └── main.py
└── README.md
```

## Getting Started

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Backend Setup

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

The backend API will be available at `http://localhost:8000`

## Environment Variables

Copy `.env.example` to `.env` in both frontend and backend directories and configure as needed.

### Frontend `.env`
- `VITE_API_URL` - Backend API URL

### Backend `.env`
- `OPENAI_API_KEY` - OpenAI API key for LangGraph
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - Application secret key

## Features

- [ ] User authentication and authorization
- [ ] Dashboard for city governance metrics
- [ ] AI-powered decision support using LangGraph
- [ ] Real-time data visualization
- [ ] Document management system
- [ ] Citizen feedback portal

## Development

This project is under active development.

## License

See LICENSE file for details.
