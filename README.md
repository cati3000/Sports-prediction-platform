# Sports Prediction Platform

A lightweight platform for predicting sports match outcomes and identifying potential betting value using real match data and team performance metrics.

## Features

- Retrieves real-time match data and bookmaker odds from external APIs
- Analyzes team form, head-to-head history, and scoring trends
- Generates predictions for upcoming fixtures using statistical methods
- Highlights betting opportunities with positive expected value (EV)

## Tech Stack

- **Backend:** Python (FastAPI)
- **Frontend:** React + Vite
- **Data Sources:** Football Data API, The Odds API
- **Approach:** Math and statistics-based analysis (no machine learning models)

## Requirements

Before running the project, make sure you have:

- Python **3.9+**
- Node.js **16+**
- API keys from:
  - [Football Data](https://www.football-data.org/client/register)
  - [The Odds API](https://the-odds-api.com/)

## Getting Started

### 1) Start the Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
uvicorn backend.app.main:app --reload --port 8000
```

### 2) Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Then open: http://localhost:5173

## Project Structure

- `backend/` — Python API and prediction/statistical logic
- `frontend/` — React-based user interface
