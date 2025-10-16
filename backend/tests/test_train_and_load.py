import os
from backend import train
from backend.predictor import Predictor


def test_train_and_load(tmp_path):
    out = tmp_path / 'player_score_model.joblib'
    # Train a small model and save to temporary path
    train.train_and_save(str(out), n=500)
    assert out.exists()

    # Copy the model into the project's models dir so Predictor can find it
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    models_dir = os.path.abspath(models_dir)
    os.makedirs(models_dir, exist_ok=True)
    target = os.path.join(models_dir, 'player_score_model.joblib')
    # Overwrite
    with open(out, 'rb') as src, open(target, 'wb') as dst:
        dst.write(src.read())

    p = Predictor()
    p.load_models()
    assert 'player_score' in p.models
    # Call predict_events to ensure no exceptions and that player candidate has prob
    results = p.predict_events('m1', 'A', 'B', {'star_player': 'X', 'recent_goals': 1, 'shots_on_target': 1.2, 'starts_last5': 4, 'xg': 0.15})
    assert any('to score' in r['event'] for r in results)
