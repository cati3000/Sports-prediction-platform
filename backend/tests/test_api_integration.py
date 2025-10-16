import os
import pytest
from backend.api_clients import FootballDataAPI, OddsAPI
from backend.features import FeatureEngine


def test_football_api_client_exists():
    """Test that Football Data API client can be instantiated"""
    api = FootballDataAPI()
    assert api is not None
    assert hasattr(api, 'get_upcoming_matches')
    assert hasattr(api, 'get_team_stats')
    assert hasattr(api, 'get_head_to_head')


def test_odds_api_client_exists():
    """Test that Odds API client can be instantiated"""
    api = OddsAPI()
    assert api is not None
    assert hasattr(api, 'get_odds')
    assert hasattr(api, 'get_player_props')


def test_feature_engine():
    """Test feature engineering functions"""
    engine = FeatureEngine()
    
    # Test odds to probability conversion
    prob = engine._odds_to_prob(2.0)
    assert prob == 0.5
    
    prob = engine._odds_to_prob(4.0)
    assert prob == 0.25


def test_feature_engine_with_mock_data():
    """Test feature computation with mock match data"""
    engine = FeatureEngine()
    
    # Mock recent matches
    recent_matches = [
        {
            'homeTeam': {'name': 'Team A'},
            'awayTeam': {'name': 'Team B'},
            'score': {'fullTime': {'home': 2, 'away': 1}}
        },
        {
            'homeTeam': {'name': 'Team C'},
            'awayTeam': {'name': 'Team A'},
            'score': {'fullTime': {'home': 0, 'away': 3}}
        }
    ]
    
    # Calculate form for Team A
    form = engine.compute_team_form(recent_matches, 'Team A', n=2)
    assert form >= 0.0
    assert form <= 3.0  # Max 3 points per game
    
    # Calculate goal stats
    goals = engine.compute_goal_stats(recent_matches, 'Team A', n=2)
    assert 'avg_goals_for' in goals
    assert 'avg_goals_against' in goals
    assert goals['avg_goals_for'] > 0  # Team A scored 5 goals total


@pytest.mark.skipif(
    not os.getenv('FOOTBALL_DATA_API_KEY'),
    reason="Requires FOOTBALL_DATA_API_KEY env var"
)
def test_real_api_call():
    """Test real API call if API key is configured (skipped if not)"""
    api = FootballDataAPI()
    matches = api.get_upcoming_matches(league='PL', days_ahead=7)
    # Should return list (empty or with matches depending on schedule)
    assert isinstance(matches, list)
