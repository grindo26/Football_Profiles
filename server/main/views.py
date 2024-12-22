from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import soccerdata as sd
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class SoccerStatsService:
    def __init__(self):
        self.fbref = sd.FBref(
            leagues="ENG-Premier League",
            seasons="2024",
            data_dir=Path("/tmp/FBref")
        )

    def fetch_player_stats(self, stat_type='standard'):
        try:
            raw_data = self.fbref.read_player_season_stats(stat_type=stat_type)
            return raw_data.reset_index()
        except ValueError:
            raise ValueError(f"Invalid stat_type: {stat_type}")

    @staticmethod
    def parse_player_data(raw_data):
        players = []
        for i in range(len(raw_data)):
            player_data = {
                "league": str(raw_data.iloc[i, 0]),
                "season": str(raw_data.iloc[i, 1]),
                "team": str(raw_data.iloc[i, 2]),
                "player": str(raw_data.iloc[i, 3]),
                "nation": str(raw_data.iloc[i, 4]),
                "pos": str(raw_data.iloc[i, 5]),
                "age": str(raw_data.iloc[i, 6]),
                "born": int(raw_data.iloc[i, 7]),
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
                    "xG": float(raw_data.iloc[i, 20]),
                    "xAG": float(raw_data.iloc[i, 22])
                },
                "progression": {
                    "PrgC": int(raw_data.iloc[i, 24]),
                    "PrgP": int(raw_data.iloc[i, 25]),
                    "PrgR": int(raw_data.iloc[i, 26])
                }
            }
            players.append(player_data)
        return players


class OpenAIService:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def generate_summary(self, player_stats):
        prompt = (
            f"Generate a concise summary for the following soccer player stats. Highlight if they are good fantasy assets too:\n"
            f"Name: {player_stats['player']}, Team: {player_stats['team']}, "
            f"Position: {player_stats['pos']}, Goals: {player_stats['performance']['Gls']}, "
            f"Assists: {player_stats['performance']['Ast']}, xG: {player_stats['expected']['xG']}, "
            f"xAG: {player_stats['expected']['xAG']}"
        )
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating summary: {str(e)}"


class PlayerSearchHandler:
    def __init__(self, stats_service, ai_service):
        self.stats_service = stats_service
        self.ai_service = ai_service

    def handle_search(self, query):
        raw_data = self.stats_service.fetch_player_stats()
        players = self.stats_service.parse_player_data(raw_data)

        if not query:
            return players[:5]

        if len(query) < 3:
            raise ValueError("Search query must be at least 3 characters long")

        filtered_players = [
            player for player in players if query.lower() in player["player"].lower()
        ]

        if not filtered_players:
            raise ValueError("Player not found")

        results = []
        for player_stats in filtered_players:
            summary = self.ai_service.generate_summary(player_stats)
            results.append({"player_stats": player_stats, "summary": summary})

        return results


# Instantiate services
stats_service = SoccerStatsService()
ai_service = OpenAIService(api_key=os.getenv('OPENAI_API_KEY'))
search_handler = PlayerSearchHandler(stats_service, ai_service)

@csrf_exempt
def search_players(request):
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()

        try:
            results = search_handler.handle_search(query)
            return JsonResponse(results, safe=False)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f"Unexpected error: {str(e)}"}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
