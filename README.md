# Soccer Player Search and Summary Generator

This project provides a web-based interface to search for soccer players and generate AI-powered summaries based on their statistics. It uses the FBRef scraper to fetch player data from the Premier League 2024 season and OpenAI's GPT API to generate natural language summaries, highlighting the player's performance and fantasy football potential.

---

## Features
- **Player Search**: Search for players by name with partial matches supported.
- **Player Statistics**: Retrieve detailed statistics for individual players, including goals, assists, expected goals (xG), and more.
- **AI-Powered Summaries**: Generate concise summaries of player performances, including insights into their fantasy football value.
- **Error Handling**: Handles invalid queries and provides meaningful error messages.

---

## Project Structure

```plaintext
.
├── main
│   ├── views.py         # Handles the search and AI-powered summary generation
│   ├── models.py        # Django models (not currently used)
│   ├── urls.py          # Routes the `search_players` endpoint
├── utils
│   ├── services.py      # Contains the `SoccerStatsService` and `OpenAIService`
│   ├── handlers.py      # Orchestrates the search logic
├── settings.py          # Django settings, including environment variable management
├── README.md            # Project documentation
```

---

## Installation

### Prerequisites
- Python 3.8+
- Django 5.1+
- OpenAI API key
- SoccerData library

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/soccer-summary.git
   cd soccer-summary
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory and add:
   ```plaintext
   OPENAI_API_KEY=your_openai_api_key
   ```

4. Run the development server:
   ```bash
   python manage.py runserver
   ```

5. Access the application at:
   ```plaintext
   http://127.0.0.1:8000/main/players
   ```

---

## API Usage

### Endpoint: `GET /main/players`
#### Query Parameters
- `q` (optional): Search query for the player name. Returns top 5 players if omitted.

#### Responses
- **Success (200)**: Returns a list of players with statistics and AI-generated summaries.
  ```json
  [
    {
      "player_stats": {
        "player": "Kevin De Bruyne",
        "team": "Manchester City",
        "pos": "MF",
        "performance": {
          "Gls": 15,
          "Ast": 20
        },
        "expected": {
          "xG": 12.3,
          "xAG": 18.5
        }
      },
      "summary": "Kevin De Bruyne, a midfielder for Manchester City, excelled with 15 goals and 20 assists, making him a top fantasy football choice."
    }
  ]
  ```
- **Error (400)**: Invalid queries or bad requests.
  ```json
  {"error": "Search query must be at least 3 characters long"}
  ```
- **Error (404)**: No players found.
  ```json
  {"error": "Player not found"}
  ```

---

## Testing

1. Run unit tests:
   ```bash
   python manage.py test
   ```

2. Example test case structure:
   - Validate data fetched by the `SoccerStatsService`
   - Mock OpenAI API responses for `OpenAIService`
   - Test search queries and response formatting in `PlayerSearchHandler`

---

## Technologies Used
- **Backend**: Django 5.1
- **Data Fetching**: SoccerData
- **AI Summaries**: OpenAI GPT API
- **Environment Management**: `python-dotenv`

---

## Future Enhancements
- Add more leagues and seasons.
- Introduce caching for faster responses.
- Enhance error handling for external API failures.
- Add a frontend interface for easier usage.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contributors
- **Your Name** - Developer ([your_email@example.com](mailto:your_email@example.com))

---

## Acknowledgements
- [FBRef](https://fbref.com) for the soccer statistics.
- [OpenAI](https://openai.com) for the language model.

