import json
from backend.predictor import Predictor

if __name__ == '__main__':
    p = Predictor()
    p.load_models()
    results = p.predict_events('m1', 'Man City', 'LowTown', {'star_player': 'Haaland'})
    print(json.dumps({'match_id': 'm1', 'candidates': results}, indent=2))
