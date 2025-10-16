# Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React/Vite)                       │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐          │
│  │   Match     │  │  Prediction  │  │    Parlay     │          │
│  │  Selector   │→ │    Panel     │→ │   Builder     │          │
│  └─────────────┘  └──────────────┘  └───────────────┘          │
│         │                  │                                     │
│    GET /matches      POST /predict                              │
└─────────┼──────────────────┼─────────────────────────────────────┘
          │                  │
          │                  │
┌─────────▼──────────────────▼─────────────────────────────────────┐
│              BACKEND API (FastAPI - Port 8000)                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  GET /matches Endpoint                                    │   │
│  │  1. Fetch upcoming fixtures                              │   │
│  │  2. Enrich with live odds                                │   │
│  │  3. Return match list                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  POST /predict Endpoint                                   │   │
│  │  1. Get match context                                    │   │
│  │  2. Fetch head-to-head data                              │   │
│  │  3. Compute features                                     │   │
│  │  4. Generate predictions                                 │   │
│  │  5. Calculate EV                                         │   │
│  │  6. Return candidates                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
          │                  │
          │                  │
    ┌─────▼─────┐      ┌────▼─────┐
    │   API     │      │ Feature  │
    │  Clients  │      │ Engine   │
    └─────┬─────┘      └────┬─────┘
          │                  │
          │                  │
┌─────────▼──────────────────▼─────────────────────────────────────┐
│                   EXTERNAL DATA SOURCES                           │
│  ┌────────────────────┐          ┌──────────────────────┐        │
│  │ football-data.org  │          │   The Odds API       │        │
│  │                    │          │                      │        │
│  │ • Match fixtures   │          │ • Live betting odds  │        │
│  │ • Team stats       │          │ • H2H markets        │        │
│  │ • Historical data  │          │ • Player props       │        │
│  │ • League standings │          │ • Multiple bookies   │        │
│  └────────────────────┘          └──────────────────────┘        │
└───────────────────────────────────────────────────────────────────┘
```

## Request Flow Example

### 1. User Loads Page
```
Browser → Frontend
  ↓
Frontend → GET /matches
  ↓
Backend → FootballDataAPI.get_upcoming_matches()
  ↓
football-data.org API → Returns fixtures
  ↓
Backend → OddsAPI.get_odds()
  ↓
The Odds API → Returns live odds
  ↓
Backend → Merge data → Return to Frontend
  ↓
Frontend → Display in MatchSelector
```

### 2. User Selects Match & Predicts
```
User clicks match → Enters player → Clicks "Predict"
  ↓
Frontend → POST /predict {match_id, home, away, context}
  ↓
Backend → Predictor.predict_events()
  ↓
├→ FootballDataAPI.get_head_to_head(match_id)
│    ↓
│   football-data.org → Returns H2H stats
│    ↓
├→ FeatureEngine.build_match_features()
│    ↓
│   Computes: form, goals, h2h, market probs
│    ↓
├→ Model predictions (if available)
│    ↓
└→ Calculate probabilities, EV, return candidates
  ↓
Frontend → Display in PredictionPanel
```

### 3. User Builds Parlay
```
User clicks "Add" on events
  ↓
Frontend → Updates parlay state
  ↓
ParlayBuilder → Calculates combined odds
  ↓
  Combined Odds = odds[0] × odds[1] × ... × odds[n]
  Combined Prob = prob[0] × prob[1] × ... × prob[n]
  Expected Return = combined_prob × (combined_odds - 1) - (1 - combined_prob)
  ↓
Display parlay summary
```

## Data Processing Pipeline

```
RAW DATA (APIs)
      │
      ▼
┌─────────────────┐
│  API Clients    │  ← Fetch & parse external data
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ Feature Engine  │  ← Transform into predictive features
│                 │
│ • Team form     │
│ • Goal stats    │
│ • H2H records   │
│ • Odds → prob   │
└─────────────────┘
      │
      ▼
┌─────────────────┐
│   Predictor     │  ← Combine features + models
│                 │
│ • Load models   │
│ • Predict probs │
│ • Calculate EV  │
└─────────────────┘
      │
      ▼
PREDICTIONS (JSON)
      │
      ▼
┌─────────────────┐
│   Frontend      │  ← Display & interact
└─────────────────┘
```

## Component Responsibilities

### Backend

| Component | Responsibility |
|-----------|----------------|
| `api_clients.py` | Fetch data from external APIs |
| `features.py` | Transform raw data → predictive features |
| `predictor.py` | Generate predictions & calculate EV |
| `app/main.py` | Expose HTTP endpoints |
| `train.py` | Train & persist ML models |

### Frontend

| Component | Responsibility |
|-----------|----------------|
| `MatchSelector` | Display upcoming matches |
| `PredictionPanel` | Get & show predictions |
| `ParlayBuilder` | Track parlay legs & compute combined odds |
| `api.js` | HTTP client for backend |

## State Management

```
Frontend State:
  ├─ matches[]        ← List of upcoming fixtures
  ├─ selectedMatch    ← Currently selected match
  ├─ predictions[]    ← Candidate events for selected match
  └─ parlayLegs[]     ← User-selected events

Backend State:
  ├─ models{}         ← Loaded ML models
  ├─ api_clients      ← Configured API clients
  └─ feature_engine   ← Feature computation engine
```

## Error Handling Flow

```
API Call
  ↓
Try:
  ↓
  API Request
  ↓
  Success? → Parse → Return
  ↓
Except:
  ↓
  Log error
  ↓
  Return empty/fallback
  ↓
Frontend:
  ↓
  Show error message or empty state
```

## Caching Strategy (Future)

```
Request → Check cache → Cache hit? → Return cached data
                ↓
            Cache miss
                ↓
         Fetch from API
                ↓
         Store in cache
                ↓
           Return data
```

## Security

- API keys stored in `.env` (not committed to git)
- CORS configured for local development
- No sensitive data stored client-side
- Rate limiting handled by external APIs

---

This architecture provides:
✅ **Separation of concerns** (API, features, prediction, UI)  
✅ **Testability** (each component can be tested independently)  
✅ **Scalability** (add more data sources easily)  
✅ **Maintainability** (clear responsibilities)
