from backend.predictor import Predictor


def test_predictor_returns_candidates():
    p = Predictor()
    p.load_models()
    results = p.predict_events('m1', 'Man City', 'LowTown', {'star_player': 'Haaland'})
    assert isinstance(results, list)
    assert len(results) >= 1
    for r in results:
        assert 'event' in r and 'prob' in r and 'odds' in r and 'ev' in r
