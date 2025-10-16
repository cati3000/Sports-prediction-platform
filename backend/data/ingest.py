import pandas as pd
from typing import List

def load_historical_matches(csv_path: str) -> pd.DataFrame:
    """Load historical match data from CSV. Expects columns like date, home, away, home_goals, away_goals."""
    df = pd.read_csv(csv_path, parse_dates=['date'])
    return df


def load_player_stats(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    return df
