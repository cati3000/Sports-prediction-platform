import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class FootballDataAPI:
    """Client for football-data.org API - real match fixtures and stats"""
    
    def __init__(self):
        self.api_key = os.getenv('FOOTBALL_DATA_API_KEY', '')
        self.base_url = 'https://api.football-data.org/v4'
        self.headers = {'X-Auth-Token': self.api_key}
    
    def get_upcoming_matches(self, league='PL', days_ahead=7) -> List[Dict[str, Any]]:
        """Get upcoming matches for a league (PL=Premier League, etc)"""
        date_from = datetime.now().strftime('%Y-%m-%d')
        date_to = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        
        url = f'{self.base_url}/competitions/{league}/matches'
        params = {'dateFrom': date_from, 'dateTo': date_to}
        
        try:
            resp = requests.get(url, headers=self.headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            matches = []
            for match in data.get('matches', []):
                matches.append({
                    'id': match['id'],
                    'home_team': match['homeTeam']['name'],
                    'away_team': match['awayTeam']['name'],
                    'date': match['utcDate'],
                    'competition': match['competition']['name']
                })
            return matches
        except Exception as e:
            print(f"Error fetching matches: {e}")
            return []
    
    def get_team_stats(self, team_id: int) -> Dict[str, Any]:
        """Get team statistics"""
        url = f'{self.base_url}/teams/{team_id}'
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error fetching team stats: {e}")
            return {}
    
    def get_head_to_head(self, match_id: int) -> Dict[str, Any]:
        """Get head-to-head stats for a match"""
        url = f'{self.base_url}/matches/{match_id}/head2head'
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error fetching h2h: {e}")
            return {}
    
    def get_team_matches(self, team_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent matches for a team to calculate real statistics"""
        url = f'{self.base_url}/teams/{team_id}/matches'
        params = {'status': 'FINISHED', 'limit': limit}
        try:
            resp = requests.get(url, headers=self.headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data.get('matches', [])
        except Exception as e:
            print(f"Error fetching team matches: {e}")
            return []
    
    def calculate_team_stats(self, team_name: str, matches: List[Dict]) -> Dict[str, Any]:
        """Calculate REAL statistics from actual match results"""
        if not matches:
            return {
                'goals_scored_avg': 1.5,
                'goals_conceded_avg': 1.2,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'form_points': 0,
                'clean_sheets': 0
            }
        
        goals_scored = []
        goals_conceded = []
        wins = 0
        draws = 0
        losses = 0
        clean_sheets = 0
        
        for match in matches:
            home_team = match.get('homeTeam', {}).get('name', '')
            away_team = match.get('awayTeam', {}).get('name', '')
            score = match.get('score', {}).get('fullTime', {})
            home_goals = score.get('home')
            away_goals = score.get('away')
            
            if home_goals is None or away_goals is None:
                continue
            
            # Determine if this team was home or away
            if home_team == team_name:
                goals_scored.append(home_goals)
                goals_conceded.append(away_goals)
                if home_goals > away_goals:
                    wins += 1
                elif home_goals == away_goals:
                    draws += 1
                else:
                    losses += 1
                if away_goals == 0:
                    clean_sheets += 1
            elif away_team == team_name:
                goals_scored.append(away_goals)
                goals_conceded.append(home_goals)
                if away_goals > home_goals:
                    wins += 1
                elif away_goals == home_goals:
                    draws += 1
                else:
                    losses += 1
                if home_goals == 0:
                    clean_sheets += 1
        
        num_matches = len(goals_scored)
        if num_matches == 0:
            return {
                'goals_scored_avg': 1.5,
                'goals_conceded_avg': 1.2,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'form_points': 0,
                'clean_sheets': 0
            }
        
        return {
            'goals_scored_avg': sum(goals_scored) / num_matches,
            'goals_conceded_avg': sum(goals_conceded) / num_matches,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'form_points': wins * 3 + draws,
            'clean_sheets': clean_sheets,
            'clean_sheet_pct': clean_sheets / num_matches
        }


class OddsAPI:
    """Client for The Odds API - real betting odds"""
    
    def __init__(self):
        self.api_key = os.getenv('ODDS_API_KEY', '')
        self.base_url = 'https://api.the-odds-api.com/v4'
    
    def get_odds(self, sport='soccer_epl', markets='h2h,spreads,totals') -> List[Dict[str, Any]]:
        """Get current odds for upcoming matches"""
        url = f'{self.base_url}/sports/{sport}/odds'
        params = {
            'apiKey': self.api_key,
            'regions': 'uk',
            'markets': markets,
            'oddsFormat': 'decimal'
        }
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error fetching odds: {e}")
            return []
    
    def get_player_props(self, sport='soccer_epl') -> List[Dict[str, Any]]:
        """Get player prop odds (goals, assists, etc)"""
        url = f'{self.base_url}/sports/{sport}/events'
        params = {
            'apiKey': self.api_key,
            'regions': 'uk',
            'markets': 'player_goal_scorer_anytime'
        }
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error fetching player props: {e}")
            return []
