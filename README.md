# Parlay Predictor - Real Data Edition

A data-driven sports prediction and parlay optimization platform that uses **real match data**, **live odds**, and **actual team statistics** to identify high-value betting opportunities.

## Features

- **Real Match Data**: Fetches upcoming fixtures from football-data.org API
- **Live Odds Integration**: Gets current betting odds from The Odds API
- **Smart Predictions**: Uses team form, head-to-head stats, and goal statistics
- **Expected Value Calculation**: Identifies bets with positive expected value
- **Parlay Optimizer**: Build multi-leg parlays with combined odds and probabilities
- **Modern UI**: Clean, betting-site-style React interface

## Prerequisites

1. **Python 3.11+** installed
2. **Node.js 18+** and npm installed
3. **API Keys** (both have free tiers):
   - Football Data: https://www.football-data.org/client/register
   - The Odds API: https://the-odds-api.com/

## Setup

### 1. Backend Setup

```powershell
cd backend

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API keys
cp .env.example .env
# Edit .env and add your API keys:
# FOOTBALL_DATA_API_KEY=your_key_here
# ODDS_API_KEY=your_key_here

# Optional: Train the player scoring model
python train.py

# Start the API server
uvicorn backend.app.main:app --reload --port 8000
```

### 2. Frontend Setup

Open a new terminal:

```powershell
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Open the URL shown (usually http://localhost:5173)

## How It Works

### Data Flow

1. **Match Data**: Fetches upcoming Premier League matches from football-data.org
2. **Odds Data**: Gets live betting odds from The Odds API
3. **Feature Engineering**: Computes team form, goal stats, h2h records
4. **Prediction**: Combines features with ML models to predict probabilities
5. **EV Calculation**: Compares predicted probabilities vs bookmaker odds
6. **Parlay Building**: Users select high-EV events to build multi-leg parlays

### API Endpoints

- `GET /matches?league=PL&days=7` - Get upcoming matches with odds
- `POST /predict` - Get predictions for a specific match

