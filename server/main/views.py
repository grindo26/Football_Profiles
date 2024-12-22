from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import soccerdata as sd
from pathlib import Path

# Initialize the FBRef scraper with Path object for data_dir
fbref = sd.FBref(leagues="ENG-Premier League", seasons="2024", data_dir=Path("/tmp/FBref"))

@csrf_exempt
def search_players(request):
    if request.method == 'GET':
        # Read the player stats DataFrame
        stat_type = 'standard'
        try:
            raw_data = fbref.read_player_season_stats(stat_type=stat_type)
        except ValueError:
            return JsonResponse({'error': f'Invalid stat_type: {stat_type}'}, status=400)

        # Reset index to include multi-index columns as part of the DataFrame
        raw_data = raw_data.reset_index()
        print(raw_data)

        # csv_file_path = "/tmp/raw_data.csv"
        # raw_data.to_csv(csv_file_path, index=False)
        # Construct JSON directly
        players_json = []
        for i in range(len(raw_data)):
            # Combine all player information into a single dictionary
            player_data = {
                "league": str(raw_data.iloc[i, 0]),
                "season": str(raw_data.iloc[i, 1]),
                "team": str(raw_data.iloc[i, 2]),
                "player": str(raw_data.iloc[i, 3]),
                "nation": str(raw_data.iloc[i, 4]),
                "pos": str(raw_data.iloc[i, 5]),
                "age": str(raw_data.iloc[i, 6]),
                "born": int(raw_data.iloc[i, 7]),
                # Nested categories
                "playing_time": {
                    "MP": int(raw_data.iloc[i, 8]),
                    "Starts": int(raw_data.iloc[i, 9]),
                    "Min": int(raw_data.iloc[i, 10]),
                    "90s": float(raw_data.iloc[i, 11])
                },
                "performance": {
                    "Gls": int(raw_data.iloc[i, 12]),
                    "Ast": int(raw_data.iloc[i, 13]),
                    "G+A": int(raw_data.iloc[i, 14]),
                    "G-PK": int(raw_data.iloc[i, 15]),
                    "PK": int(raw_data.iloc[i, 16]),
                    "PKatt": int(raw_data.iloc[i, 17]),
                    "CrdY": int(raw_data.iloc[i, 18]),
                    "CrdR": int(raw_data.iloc[i, 19])
                },
                "expected": {
                    "xG": int(raw_data.iloc[i, 20]),
                    "npxG": int(raw_data.iloc[i, 21]),
                    "xAG": int(raw_data.iloc[i, 22]),
                    "npxG+xAG": int(raw_data.iloc[i, 23])
                },
                "progression": {
                    "PrgC": int(raw_data.iloc[i, 24]),
                    "PrgP": int(raw_data.iloc[i, 25]),
                    "PrgR": int(raw_data.iloc[i, 26])
                },
                "per_90_minutes": {
                    "Gls": int(raw_data.iloc[i, 27]),
                    "Ast": int(raw_data.iloc[i, 28]),
                    "G+A": int(raw_data.iloc[i, 29]),
                    "G-PK": int(raw_data.iloc[i, 30]),
                    "G+A-PK": int(raw_data.iloc[i, 31]),
                    "xG": int(raw_data.iloc[i, 32]),
                    "xAG": int(raw_data.iloc[i, 33]),
                    "xG+xAG": int(raw_data.iloc[i, 34]),
                    "npxG": int(raw_data.iloc[i, 35]),
                    "npxG+xAG": int(raw_data.iloc[i, 36])
                }
            }
            players_json.append(player_data)

        query = request.GET.get('q', '').strip()

        # If no query, return the top 5 players
        if not query:
            return JsonResponse(players_json[:5], safe=False)

        # Validate query length
        if len(query) < 3:
            return JsonResponse({'error': 'Search query must be at least 3 characters long'}, status=400)

        # Filter players by name
        filtered_players = [
            player for player in players_json if query.lower() in player["player"].lower()
        ]

        # Return filtered players
        return JsonResponse(filtered_players, safe=False)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
