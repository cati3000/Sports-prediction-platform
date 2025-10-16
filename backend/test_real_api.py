from api_clients import FootballDataAPI

api = FootballDataAPI()
matches = api.get_upcoming_matches(league='PL', days_ahead=14)

print(f'\n✅ REAL MATCH DATA FROM API:')
print(f'Found {len(matches)} upcoming Premier League matches:\n')

for i, m in enumerate(matches[:10], 1):
    print(f"{i}. {m['home_team']} vs {m['away_team']}")
    print(f"   Date: {m['date']}")
    print(f"   Competition: {m['competition']}\n")
