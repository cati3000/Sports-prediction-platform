# Quick Start Guide

## IMPORTANT: Get Your API Keys First!

### 1. Football-data.org API Key (FREE)
1. Go to: https://www.football-data.org/client/register
2. Sign up with your email
3. You'll receive your API key immediately
4. Free tier: 10 calls/minute, perfect for testing

### 2. The Odds API Key (FREE)
1. Go to: https://the-odds-api.com/
2. Click "Get a Free API Key"
3. Sign up with your email
4. Free tier: 500 calls/month

## Setup (5 minutes)

### Backend

```powershell
# 1. Go to backend folder
cd C:\Users\Catalin\Desktop\proj_parlay\backend

# 2. Activate virtual environment (if not already active)
..\.venv\Scripts\Activate.ps1

# 3. Install new dependencies
pip install requests python-dotenv

# 4. Create .env file from example
cp .env.example .env

# 5. Edit .env and add your API keys
notepad .env
# Add your actual keys:
# FOOTBALL_DATA_API_KEY=your_actual_key_here
# ODDS_API_KEY=your_actual_key_here

# 6. Start the backend
uvicorn backend.app.main:app --reload --port 8000
```

### Frontend (separate terminal)

```powershell
# 1. Go to frontend folder
cd C:\Users\Catalin\Desktop\proj_parlay\frontend

# 2. Start frontend (dependencies already installed)
npm run dev
```

## What You'll See

1. **Backend**: API running at http://localhost:8000
   - Visit http://localhost:8000/docs for API documentation

2. **Frontend**: React app at http://localhost:5173
   - **Left panel**: Real upcoming Premier League matches
   - **Middle**: Click a match → Enter player name → Click "Predict"
   - **Right**: Build your parlay by adding high-EV events

## How to Use

1. **Select a Match**: Click on any upcoming match in the list
2. **Enter Player Name**: Type a star player's name (e.g., "Haaland", "Salah")
3. **Get Predictions**: Click "Predict" to see:
   - Win probabilities for both teams
   - Player scoring probability
   - Real odds from bookmakers
   - Expected Value (EV) for each bet
4. **Build Parlay**: Click "Add" on high-EV events
5. **See Combined Odds**: The right panel shows your parlay's total odds and probability

## Troubleshooting

### "Could not load matches"
- Check that backend is running (http://localhost:8000)
- Make sure you added your API keys to `.env`
- Check console for specific error messages

### "Failed to reach backend"
- Backend must be running before using frontend
- Check that port 8000 is not in use by another app

### No matches showing
- Free API keys might have rate limits
- Try again in a minute
- Check that your API keys are valid

## What's Real vs What's Simulated

### REAL DATA:
✅ Upcoming match fixtures (from football-data.org)
✅ Live betting odds (from The Odds API)
✅ Team names, dates, competitions
✅ Head-to-head statistics
✅ Team form calculations

### STILL NEEDS WORK:
⚠️ Player statistics (need more detailed APIs or scraping)
⚠️ xG (expected goals) data (requires paid APIs like Opta)
⚠️ Injury/suspension data
⚠️ Historical model training on large datasets

The predictions use a combination of:
- Real odds-implied probabilities
- Simple team form heuristics
- A basic ML model (trained on synthetic data for now)

## Next Steps to Make It Better

1. **Get more data**: Add player stats APIs, injury reports
2. **Train on real history**: Download historical match CSVs and retrain models
3. **Add more leagues**: Support La Liga, Serie A, etc.
4. **Improve features**: Add venue, rest days, referee data
5. **Backtest**: Validate predictions against historical results

---

**You now have a working app with real matches and real odds!** 🎉
