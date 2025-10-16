from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.predictor import Predictor
from backend.api_clients import FootballDataAPI, OddsAPI
from datetime import datetime, timedelta

app = FastAPI(title="Parlay Predictor API")

# Add CORS middleware so frontend can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for matches
matches_cache = {}
cache_timestamp = {}
CACHE_DURATION = timedelta(minutes=5)  # Cache for 5 minutes

class PredictRequest(BaseModel):
    match_id: str
    home_team: str
    away_team: str
    context: dict = {}

predictor = Predictor()
football_api = FootballDataAPI()
odds_api = OddsAPI()

@app.on_event("startup")
async def startup_event():
    # Load models and initialize APIs
    predictor.load_models()

@app.get("/matches")
async def get_upcoming_matches(league: str = "ALL", days: int = 14):
    """Get real upcoming matches from football-data.org
    
    Supported leagues:
    - PL: Premier League (England)
    - PD: La Liga (Spain)  
    - BL1: Bundesliga (Germany)
    - SA: Serie A (Italy)
    - FL1: Ligue 1 (France)
    - ALL: All top 5 leagues
    """
    
    # Check cache
    cache_key = f"{league}_{days}"
    now = datetime.now()
    
    if cache_key in matches_cache and cache_key in cache_timestamp:
        if now - cache_timestamp[cache_key] < CACHE_DURATION:
            print(f"[CACHE HIT] Returning cached matches for {league}")
            return matches_cache[cache_key]
    
    print(f"[CACHE MISS] Fetching fresh matches for {league}")
    
    # Top 5 European leagues
    if league == "ALL":
        leagues = ["PL", "PD", "BL1", "SA", "FL1"]
        all_matches = []
        for lg in leagues:
            matches = football_api.get_upcoming_matches(league=lg, days_ahead=days)
            all_matches.extend(matches)
            # Cache individual leagues too
            individual_result = {"matches": matches, "total": len(matches)}
            individual_cache_key = f"{lg}_{days}"
            matches_cache[individual_cache_key] = individual_result
            cache_timestamp[individual_cache_key] = now
        matches = all_matches
    else:
        matches = football_api.get_upcoming_matches(league=league, days_ahead=days)
    
    # Try to enrich with odds data
    try:
        odds_list = odds_api.get_odds(sport='soccer_epl')
        # Match odds to fixtures by team names (simple matching)
        odds_map = {}
        for game in odds_list:
            key = f"{game.get('home_team', '')}_{game.get('away_team', '')}"
            if 'bookmakers' in game and game['bookmakers']:
                bookmaker = game['bookmakers'][0]
                if 'markets' in bookmaker and bookmaker['markets']:
                    market = bookmaker['markets'][0]
                    if 'outcomes' in market:
                        outcomes = {o['name']: o['price'] for o in market['outcomes']}
                        odds_map[key] = outcomes
        
        # Enrich matches with odds
        for match in matches:
            key = f"{match['home_team']}_{match['away_team']}"
            if key in odds_map:
                match['odds'] = odds_map[key]
    except Exception as e:
        print(f"Could not fetch odds: {e}")
    
    # Store in cache
    result = {"matches": matches, "total": len(matches)}
    matches_cache[cache_key] = result
    cache_timestamp[cache_key] = now
    
    return result

@app.post("/predict")
async def predict(req: PredictRequest):
    # Return top candidate events with probability and implied payout
    results = predictor.predict_events(req.match_id, req.home_team, req.away_team, req.context)
    return {"match_id": req.match_id, "candidates": results}
