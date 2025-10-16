import numpy as np
from typing import List, Dict, Any
from collections import defaultdict

class FeatureEngine:
    """Build predictive features from real match and team data"""
    
    def __init__(self):
        self.team_cache = {}
        
    def compute_team_form(self, recent_matches: List[Dict], team_name: str, n=5) -> float:
        """Compute team form from last N matches (points per game)"""
        points = []
        for match in recent_matches[:n]:
            if match['homeTeam']['name'] == team_name:
                result = self._get_result(match['score']['fullTime']['home'], 
                                         match['score']['fullTime']['away'], 
                                         is_home=True)
                points.append(result)
            elif match['awayTeam']['name'] == team_name:
                result = self._get_result(match['score']['fullTime']['away'],
                                         match['score']['fullTime']['home'],
                                         is_home=False)
                points.append(result)
        
        return np.mean(points) if points else 1.0  # default to 1.0 (draw form)
    
    def _get_result(self, goals_for: int, goals_against: int, is_home: bool) -> float:
        """Convert match result to points (3=win, 1=draw, 0=loss)"""
        if goals_for > goals_against:
            return 3.0
        elif goals_for == goals_against:
            return 1.0
        return 0.0
    
    def compute_head_to_head(self, h2h_data: Dict) -> Dict[str, float]:
        """Extract h2h win rates"""
        if not h2h_data or 'matches' not in h2h_data:
            return {'home_h2h_wr': 0.5, 'away_h2h_wr': 0.5}
        
        home_wins = 0
        away_wins = 0
        total = len(h2h_data['matches'])
        
        for match in h2h_data['matches']:
            if match.get('score', {}).get('winner') == 'HOME_TEAM':
                home_wins += 1
            elif match.get('score', {}).get('winner') == 'AWAY_TEAM':
                away_wins += 1
        
        return {
            'home_h2h_wr': home_wins / max(total, 1),
            'away_h2h_wr': away_wins / max(total, 1)
        }
    
    def compute_goal_stats(self, recent_matches: List[Dict], team_name: str, n=10) -> Dict[str, float]:
        """Compute goals scored/conceded per game"""
        goals_for = []
        goals_against = []
        
        for match in recent_matches[:n]:
            if match['homeTeam']['name'] == team_name:
                goals_for.append(match['score']['fullTime']['home'])
                goals_against.append(match['score']['fullTime']['away'])
            elif match['awayTeam']['name'] == team_name:
                goals_for.append(match['score']['fullTime']['away'])
                goals_against.append(match['score']['fullTime']['home'])
        
        return {
            'avg_goals_for': np.mean(goals_for) if goals_for else 1.0,
            'avg_goals_against': np.mean(goals_against) if goals_against else 1.0
        }
    
    def build_match_features(self, home_team: str, away_team: str, 
                            home_recent: List[Dict], away_recent: List[Dict],
                            h2h_data: Dict, odds_data: Dict = None) -> Dict[str, float]:
        """Build complete feature set for a match"""
        features = {}
        
        # Form features
        features['home_form'] = self.compute_team_form(home_recent, home_team)
        features['away_form'] = self.compute_team_form(away_recent, away_team)
        
        # Goal stats
        home_goals = self.compute_goal_stats(home_recent, home_team)
        away_goals = self.compute_goal_stats(away_recent, away_team)
        features.update({f'home_{k}': v for k, v in home_goals.items()})
        features.update({f'away_{k}': v for k, v in away_goals.items()})
        
        # H2H
        h2h = self.compute_head_to_head(h2h_data)
        features.update(h2h)
        
        # Odds-implied probabilities if available
        if odds_data:
            features['market_prob_home'] = self._odds_to_prob(odds_data.get('home_odds', 2.0))
            features['market_prob_away'] = self._odds_to_prob(odds_data.get('away_odds', 3.0))
        
        return features
    
    def _odds_to_prob(self, odds: float) -> float:
        """Convert decimal odds to implied probability"""
        return 1.0 / max(odds, 1.01)
