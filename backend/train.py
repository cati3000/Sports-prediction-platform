import argparse
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'player_score_model.joblib')


def make_synthetic_player_dataset(n=2000, random_state=42):
    rng = np.random.RandomState(random_state)
    # Features: recent_goals, shots_on_target_per90, starts_last5, xG_per90
    recent_goals = rng.poisson(0.3, size=n)
    shots_on_target = rng.normal(0.8 + recent_goals * 0.5, 0.5, size=n)
    starts_last5 = rng.randint(0, 6, size=n)
    xg = np.clip(rng.normal(0.1 + recent_goals * 0.05, 0.05, size=n), 0, None)
    # label: player scores in next match (prob increases with recent_goals, shots, xg)
    logits = -2.0 + 0.6 * recent_goals + 0.8 * shots_on_target + 3.0 * xg + 0.2 * starts_last5
    probs = 1.0 / (1.0 + np.exp(-logits))
    labels = rng.binomial(1, probs)
    df = pd.DataFrame({
        'recent_goals': recent_goals,
        'shots_on_target': shots_on_target,
        'starts_last5': starts_last5,
        'xg': xg,
        'label': labels,
    })
    return df


def train_and_save(model_path=MODEL_PATH, n=2000):
    df = make_synthetic_player_dataset(n=n)
    X = df[['recent_goals', 'shots_on_target', 'starts_last5', 'xg']]
    y = df['label']
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=1)
    model = GradientBoostingClassifier(n_estimators=50, random_state=1)
    model.fit(X_train, y_train)
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    print(f"Saved model to {model_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', '-o', default=MODEL_PATH)
    parser.add_argument('--n', type=int, default=2000)
    args = parser.parse_args()
    train_and_save(args.out, n=args.n)


if __name__ == '__main__':
    main()
