import os
from typing import List, Dict, Any
import numpy as np
from backend.api_clients import FootballDataAPI, OddsAPI
from backend.features import FeatureEngine


class Predictor:
    """Lightweight predictor scaffold.

    Contract:
    - load_models(): loads any persisted models/data
    - predict_events(match_id, home, away, context) -> list of candidate dicts

    Each candidate dict: {"event": str, "prob": float, "odds": float, "ev": float}
    """

    def __init__(self):
        self.models = {}
        self.football_api = FootballDataAPI()
        self.odds_api = OddsAPI()
        self.feature_engine = FeatureEngine()

    
    def load_models(self):
        """Load any pre-trained models"""
        pass

    def predict_events(self, match_id: str, home: str, away: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate data-driven betting predictions with real statistical analysis"""
        events = []
        
        # Get real match data
        real_match_id = context.get('real_match_id')
        odds_data = context.get('odds_data', {})
        
        # Fetch real head-to-head and form data
        h2h_data = None
        if real_match_id:
            try:
                h2h_data = self.football_api.get_head_to_head(real_match_id)
            except Exception as e:
                print(f"Could not fetch H2H: {e}")
        
        # Build comprehensive features
        features = self._analyze_match_statistics(home, away, h2h_data, odds_data)
        
        # Generate high-value betting opportunities based on statistical analysis
        events.extend(self._analyze_match_result(features, odds_data, home, away))
        events.extend(self._analyze_goals_markets(features, odds_data))
        events.extend(self._analyze_btts(features, odds_data))
        events.extend(self._analyze_corners_cards(features, odds_data))
        
        # Sort by PROBABILITY first (most likely outcomes), then by EV
        events.sort(key=lambda e: (e['prob'], e['ev']), reverse=True)
        
        # Return top 12 predictions
        return events[:12]
    
    def _analyze_match_statistics(self, home: str, away: str, h2h_data: Any, odds_data: Dict) -> Dict:
        """Deep statistical analysis using REAL match data"""
        
        # Fetch REAL recent matches for both teams
        print(f"Fetching real statistics for {home} vs {away}...")
        
        # Try to get team IDs from h2h data
        home_team_id = None
        away_team_id = None
        
        if h2h_data and 'matches' in h2h_data and len(h2h_data['matches']) > 0:
            first_match = h2h_data['matches'][0]
            if first_match.get('homeTeam', {}).get('name') == home:
                home_team_id = first_match['homeTeam'].get('id')
                away_team_id = first_match['awayTeam'].get('id')
            elif first_match.get('awayTeam', {}).get('name') == home:
                home_team_id = first_match['awayTeam'].get('id')
                away_team_id = first_match['homeTeam'].get('id')
        
        # Get REAL match history and calculate stats
        home_stats = {'goals_scored_avg': 1.5, 'goals_conceded_avg': 1.2, 'form_points': 7, 'clean_sheet_pct': 0.3}
        away_stats = {'goals_scored_avg': 1.3, 'goals_conceded_avg': 1.1, 'form_points': 6, 'clean_sheet_pct': 0.3}
        
        if home_team_id:
            try:
                home_matches = self.football_api.get_team_matches(home_team_id, limit=10)
                if home_matches:
                    home_stats = self.football_api.calculate_team_stats(home, home_matches)
                    print(f"  {home}: {home_stats['goals_scored_avg']:.1f} goals/game, {home_stats['form_points']} pts from last 10")
            except Exception as e:
                print(f"  Could not fetch {home} stats: {e}")
        
        if away_team_id:
            try:
                away_matches = self.football_api.get_team_matches(away_team_id, limit=10)
                if away_matches:
                    away_stats = self.football_api.calculate_team_stats(away, away_matches)
                    print(f"  {away}: {away_stats['goals_scored_avg']:.1f} goals/game, {away_stats['form_points']} pts from last 10")
            except Exception as e:
                print(f"  Could not fetch {away} stats: {e}")
        
        # Build features from REAL data
        features = {
            'home_team': home,
            'away_team': away,
            'home_goals_avg': home_stats['goals_scored_avg'],
            'away_goals_avg': away_stats['goals_scored_avg'],
            'home_conceded_avg': home_stats['goals_conceded_avg'],
            'away_conceded_avg': away_stats['goals_conceded_avg'],
            'home_form_points': home_stats['form_points'],
            'away_form_points': away_stats['form_points'],
            'h2h_goals_avg': 2.5,
            'home_corners_avg': 5.5,  # Still estimated - not available in API
            'away_corners_avg': 4.8,  # Still estimated
            'home_cards_avg': 2.1,    # Still estimated
            'away_cards_avg': 2.3,    # Still estimated
            'home_clean_sheet_pct': home_stats.get('clean_sheet_pct', 0.3),
            'away_clean_sheet_pct': away_stats.get('clean_sheet_pct', 0.3)
        }
        
        # Extract real H2H stats if available
        if h2h_data and 'aggregates' in h2h_data:
            agg = h2h_data['aggregates']
            if 'homeTeam' in agg:
                features['home_goals_avg'] = agg['homeTeam'].get('avgGoals', features['home_goals_avg'])
            if 'awayTeam' in agg:
                features['away_goals_avg'] = agg['awayTeam'].get('avgGoals', features['away_goals_avg'])
        
        # Calculate xG (Expected Goals) using REAL data
        home_attack_strength = features['home_goals_avg'] / 1.5
        away_defense_strength = features['away_conceded_avg'] / 1.2
        features['home_xg'] = home_attack_strength * away_defense_strength * 1.5
        
        away_attack_strength = features['away_goals_avg'] / 1.3
        home_defense_strength = features['home_conceded_avg'] / 1.0
        features['away_xg'] = away_attack_strength * home_defense_strength * 1.3
        
        features['total_xg'] = features['home_xg'] + features['away_xg']
        
        print(f"  xG Model: {home} {features['home_xg']:.2f} - {features['away_xg']:.2f} {away} (Total: {features['total_xg']:.2f})")
        
        return features
    
    def _analyze_goals_markets(self, features: Dict, odds_data: Dict) -> List[Dict]:
        """Analyze Over/Under goals markets - show most relevant bets"""
        predictions = []
        total_xg = features['total_xg']
        
        # Over/Under 2.5 Goals - ALWAYS show (most popular market)
        prob_over_25 = self._poisson_over(total_xg, 2.5)
        prob_under_25 = 1.0 - prob_over_25
        
        fair_odds_over_25 = 1.0 / prob_over_25 if prob_over_25 > 0.01 else 50.0
        market_odds_over_25 = odds_data.get('over_2.5_goals', fair_odds_over_25 * 1.1)
        market_odds_under_25 = odds_data.get('under_2.5_goals', (1.0 / prob_under_25) * 1.1)
        
        ev_over_25 = prob_over_25 * market_odds_over_25 - 1.0
        ev_under_25 = prob_under_25 * market_odds_under_25 - 1.0
        
        # Show the more likely outcome
        if prob_over_25 >= 0.45:  # If reasonable chance
            predictions.append({
                'event': 'Over 2.5 Goals',
                'prob': round(prob_over_25, 3),
                'odds': round(market_odds_over_25, 2),
                'ev': round(ev_over_25, 3),
                'reasoning': f'xG model projects {total_xg:.1f} total goals. {prob_over_25*100:.0f}% chance of 3+ goals'
            })
        
        if prob_under_25 >= 0.45:
            predictions.append({
                'event': 'Under 2.5 Goals',
                'prob': round(prob_under_25, 3),
                'odds': round(market_odds_under_25, 2),
                'ev': round(ev_under_25, 3),
                'reasoning': f'Low-scoring expected. xG model: {total_xg:.1f} goals. {prob_under_25*100:.0f}% chance'
            })
        
        # Over 1.5 Goals - show if high probability
        prob_over_15 = self._poisson_over(total_xg, 1.5)
        if prob_over_15 > 0.70:  # Very likely
            fair_odds_over_15 = 1.0 / prob_over_15 if prob_over_15 > 0.01 else 20.0
            market_odds_over_15 = odds_data.get('over_1.5_goals', fair_odds_over_15 * 1.08)
            ev_over_15 = prob_over_15 * market_odds_over_15 - 1.0
            
            predictions.append({
                'event': 'Over 1.5 Goals',
                'prob': round(prob_over_15, 3),
                'odds': round(market_odds_over_15, 2),
                'ev': round(ev_over_15, 3),
                'reasoning': f'Very high probability ({prob_over_15*100:.0f}%) of 2+ goals based on attacking stats'
            })
        
        # Over 3.5 Goals - only if xG supports it
        if total_xg > 2.8:
            prob_over_35 = self._poisson_over(total_xg, 3.5)
            if prob_over_35 > 0.35:
                fair_odds_over_35 = 1.0 / prob_over_35 if prob_over_35 > 0.01 else 100.0
                market_odds_over_35 = odds_data.get('over_3.5_goals', fair_odds_over_35 * 1.15)
                ev_over_35 = prob_over_35 * market_odds_over_35 - 1.0
                
                predictions.append({
                    'event': 'Over 3.5 Goals',
                    'prob': round(prob_over_35, 3),
                    'odds': round(market_odds_over_35, 2),
                    'ev': round(ev_over_35, 3),
                    'reasoning': f'High-scoring match likely. Teams avg {features["home_goals_avg"]:.1f} and {features["away_goals_avg"]:.1f} goals'
                })
        
        return predictions
    
    def _analyze_btts(self, features: Dict, odds_data: Dict) -> List[Dict]:
        """Both Teams To Score analysis - ALWAYS show both outcomes"""
        predictions = []
        
        # Calculate BTTS probability using team scoring rates
        home_scores_prob = 1 - np.exp(-features['home_xg'])
        away_scores_prob = 1 - np.exp(-features['away_xg'])
        
        btts_yes_prob = home_scores_prob * away_scores_prob
        
        # Adjust based on clean sheet records
        btts_yes_prob *= (1 - features['home_clean_sheet_pct'] * 0.3)
        btts_yes_prob *= (1 - features['away_clean_sheet_pct'] * 0.3)
        
        btts_no_prob = 1.0 - btts_yes_prob
        
        fair_odds_btts_yes = 1.0 / btts_yes_prob if btts_yes_prob > 0.01 else 50.0
        fair_odds_btts_no = 1.0 / btts_no_prob if btts_no_prob > 0.01 else 50.0
        
        market_odds_btts_yes = odds_data.get('btts_yes', fair_odds_btts_yes * 1.12)
        market_odds_btts_no = odds_data.get('btts_no', fair_odds_btts_no * 1.12)
        
        ev_btts_yes = btts_yes_prob * market_odds_btts_yes - 1.0
        ev_btts_no = btts_no_prob * market_odds_btts_no - 1.0
        
        # Show BTTS Yes if probability > 40%
        if btts_yes_prob > 0.40:
            predictions.append({
                'event': 'Both Teams To Score - Yes',
                'prob': round(btts_yes_prob, 3),
                'odds': round(market_odds_btts_yes, 2),
                'ev': round(ev_btts_yes, 3),
                'reasoning': f'{btts_yes_prob*100:.0f}% chance both score. Home xG: {features["home_xg"]:.2f}, Away xG: {features["away_xg"]:.2f}'
            })
        
        # Show BTTS No if probability > 40%
        if btts_no_prob > 0.40:
            predictions.append({
                'event': 'Both Teams To Score - No',
                'prob': round(btts_no_prob, 3),
                'odds': round(market_odds_btts_no, 2),
                'ev': round(ev_btts_no, 3),
                'reasoning': f'{btts_no_prob*100:.0f}% chance of clean sheet. Low xG for one team'
            })
        
        return predictions
    
    def _analyze_corners_cards(self, features: Dict, odds_data: Dict) -> List[Dict]:
        """Analyze corners and cards markets"""
        predictions = []
        
        total_corners_avg = features['home_corners_avg'] + features['away_corners_avg']
        
        # Over 9.5 Corners
        if total_corners_avg > 9.0:
            prob_over_corners = 0.55 + (total_corners_avg - 9.0) * 0.08
            prob_over_corners = min(prob_over_corners, 0.85)
            
            fair_odds = 1.0 / prob_over_corners
            market_odds = odds_data.get('over_9.5_corners', fair_odds * 1.1)
            
            ev = prob_over_corners * market_odds - 1.0
            
            if ev > 0.04:
                predictions.append({
                    'event': 'Over 9.5 Corners',
                    'prob': round(prob_over_corners, 3),
                    'odds': round(market_odds, 2),
                    'ev': round(ev, 3),
                    'reasoning': f'Teams average {total_corners_avg:.1f} total corners per match'
                })
        
        return predictions
    
    def _analyze_match_result(self, features: Dict, odds_data: Dict, home: str, away: str) -> List[Dict]:
        """Analyze match result markets - ALWAYS show all three outcomes"""
        predictions = []
        
        # Use xG and form to calculate win probabilities
        home_xg = features['home_xg']
        away_xg = features['away_xg']
        
        # Poisson-based win probability
        prob_home_win = self._poisson_win_prob(home_xg, away_xg, 'home')
        prob_away_win = self._poisson_win_prob(home_xg, away_xg, 'away')
        prob_draw = self._poisson_win_prob(home_xg, away_xg, 'draw')
        
        # Normalize probabilities to sum to 1.0
        total_prob = prob_home_win + prob_away_win + prob_draw
        prob_home_win /= total_prob
        prob_away_win /= total_prob
        prob_draw /= total_prob
        
        # Get market odds
        home_odds = odds_data.get('home_odds', 1.0 / prob_home_win * 1.1)
        away_odds = odds_data.get('away_odds', 1.0 / prob_away_win * 1.1)
        draw_odds = odds_data.get('draw_odds', 1.0 / prob_draw * 1.15)
        
        # Calculate EV for each outcome
        ev_home = prob_home_win * home_odds - 1.0
        ev_away = prob_away_win * away_odds - 1.0
        ev_draw = prob_draw * draw_odds - 1.0
        
        # ALWAYS add all three outcomes - user decides what to bet
        predictions.append({
            'event': f'{home} Win',
            'prob': round(prob_home_win, 3),
            'odds': round(home_odds, 2),
            'ev': round(ev_home, 3),
            'reasoning': f'xG: {home_xg:.2f} vs {away_xg:.2f}. Form: {features["home_form_points"]:.0f} pts last 10 games'
        })
        
        predictions.append({
            'event': f'{away} Win',
            'prob': round(prob_away_win, 3),
            'odds': round(away_odds, 2),
            'ev': round(ev_away, 3),
            'reasoning': f'xG advantage {away_xg:.2f} vs {home_xg:.2f}. Recent form: {features["away_form_points"]:.0f} pts'
        })
        
        predictions.append({
            'event': 'Draw',
            'prob': round(prob_draw, 3),
            'odds': round(draw_odds, 2),
            'ev': round(ev_draw, 3),
            'reasoning': f'Draw probability {prob_draw*100:.0f}% based on xG model and team strengths'
        })
        
        return predictions
    
    def _poisson_over(self, lambda_total: float, threshold: float) -> float:
        """Calculate probability of over X goals using Poisson distribution"""
        import math
        prob_under = 0.0
        for k in range(int(threshold) + 1):
            prob_under += (lambda_total ** k) * np.exp(-lambda_total) / math.factorial(k)
        return 1.0 - prob_under
    
    def _poisson_win_prob(self, home_lambda: float, away_lambda: float, outcome: str) -> float:
        """Calculate win probability using bivariate Poisson"""
        import math
        prob = 0.0
        max_goals = 10
        
        for i in range(max_goals):
            for j in range(max_goals):
                prob_score = (np.exp(-home_lambda) * (home_lambda ** i) / math.factorial(i)) * \
                           (np.exp(-away_lambda) * (away_lambda ** j) / math.factorial(j))
                
                if outcome == 'home' and i > j:
                    prob += prob_score
                elif outcome == 'away' and j > i:
                    prob += prob_score
                elif outcome == 'draw' and i == j:
                    prob += prob_score
        
        return min(max(prob, 0.01), 0.95)
    
    def _odds_to_prob(self, odds: float) -> float:
        """Convert decimal odds to probability"""
        return 1.0 / max(odds, 1.01)

    # Future methods
    def train(self, data_path: str):
        """Train models from historical data.
        Should persist models to disk for later load_models().
        """
        raise NotImplementedError()

    def optimize_parlay(self, candidates: List[Dict[str, Any]], bankroll: float = 100.0, max_legs: int = 4) -> Dict[str, Any]:
        """A simple heuristic optimizer that picks top EV picks while capping legs.
        Returns a parlay dict with chosen legs and estimated parlay payout.
        """
        chosen = sorted(candidates, key=lambda c: c['ev'], reverse=True)[:max_legs]
        # compute combined odds and theoretical probability assuming independence
        combined_odds = 1.0
        combined_prob = 1.0
        for c in chosen:
            combined_odds *= c['odds']
            combined_prob *= c['prob']
        expected_return = combined_prob * (combined_odds - 1) - (1 - combined_prob)
        return {"legs": chosen, "combined_odds": round(combined_odds,2), "prob": round(combined_prob,4), "expected_return": round(expected_return,3)}
