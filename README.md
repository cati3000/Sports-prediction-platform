# Sports Prediction Platform

A simple tool to predict sports match outcomes and find good betting opportunities using real match data and team statistics.

## What it does

- Pulls real match data and odds from APIs
- Analyzes team form, head-to-head records, and goal statistics  
- Makes predictions for upcoming matches
- Shows you bets with good expected value

## Getting started

### Requirements

- Python 3.9+
- Node.js 16+
- Free API keys from:
  - [Football Data](https://www.football-data.org/client/register)
  - [The Odds API](https://the-odds-api.com/)

### Setup

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
uvicorn backend.app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173

## How it works

1. Fetches upcoming Premier League matches
2. Gets live odds from bookmakers
3. Calculates team stats (form, goals, head-to-head)
4. Predicts match outcomes
5. Compares predictions to odds to find value bets

## Project structure

- `backend/` - Python API with predictions
- `frontend/` - React UI
- `models/` - Trained ML models