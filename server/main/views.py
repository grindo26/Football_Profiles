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
        keys = [
            "league", "season", "team", "player", "nation", "pos", "age", "born",
            "MP", "Starts", "Min", "90s",
            "Gls", "Ast", "G+A", "G-PK", "PK", "PKatt", "CrdY", "CrdR",
            "xG", "xAG", "PrgC", "PrgP", "PrgR",
            "per_90_Gls", "per_90_Ast", "per_90_G+A", "per_90_G-PK", "per_90_G+A-PK",
            "per_90_xG", "per_90_xAG", "per_90_xG+xAG", "per_90_npxG", "per_90_npxG+xAG"
        ]

        def create_nested_dict(row):
            return {
                keys[i]: (
                    float(row[i]) if isinstance(row[i], (float, int)) and i > 7 else str(row[i])
                ) if i < 8 else {
                    "playing_time": {k: int(row[j]) for j, k in enumerate(keys[8:12], 8)},
                    "performance": {
                        **{k: int(row[j]) for j, k in enumerate(keys[12:20], 12)},
                        **{k: float(row[j]) for j, k in enumerate(keys[20:22], 20)}
                    },
                    "progression": {k: int(row[j]) for j, k in enumerate(keys[22:25], 22)},
                    "per_90_minutes": {k.split('_')[2]: float(row[j]) for j, k in enumerate(keys[25:], 25)}
                }[keys[i]]
            }

        return [create_nested_dict(raw_data.iloc[i]) for i in range(len(raw_data))]


class OpenAIService:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def generate_summary(self, player_stats):
        prompt = (
            f"Generate a concise summary for the following soccer player stats. Highlight if they are good fantasy assets too:\n"
            f"Name: {player_stats['player']}, Team: {player_stats['team']}, "
            f"Position: {player_stats['pos']}, Goals: {player_stats['performance']['Gls']}, "
            f"Assists: {player_stats['performance']['Ast']}, xG: {player_stats['performance']['xG']}, "
            f"xAG: {player_stats['performance']['xAG']}, Goals per 90 minutes: {player_stats['per_90_minutes']['Gls']}, "
            f"Assists per 90 minutes: {player_stats['per_90_minutes']['Ast']}"
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
