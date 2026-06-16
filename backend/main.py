from fastapi import FastAPI, HTTPException
from nba_api.stats.endpoints import leaguestandings, playercareerstats, teamyearbyyearstats, scoreboardv3
from cachetools import TTLCache
from models import TeamStanding, PlayerSeasonStats, TeamSeasonStats, GameInfo
from datetime import date

app = FastAPI()

cache_standings = TTLCache(maxsize=1, ttl=3600)
cache_players = TTLCache(maxsize=100, ttl=86400)
cache_teams = TTLCache(maxsize=30, ttl=86400)
cache_live_games =TTLCache(maxsize=1, ttl=15)
cache_historical_games = TTLCache(maxsize=30, ttl=86400)

@app.get("/standings", response_model=list[TeamStanding])
def get_classification():

    if "actual_standings" in cache_standings:
        return cache_standings.get("actual_standings")
    
    petition = leaguestandings.LeagueStandings()
    df = petition.get_data_frames()[0]
    clean_data = df.to_dict(orient="records")

    cache_standings["actual_standings"] = clean_data
    return clean_data

@app.get("/player/{player_id}/stats", response_model=PlayerSeasonStats)
def get_stats(player_id: int):
    if player_id in cache_players.keys():
        return cache_players.get(player_id)
    
    try:
        petition = playercareerstats.PlayerCareerStats(player_id)
        df = petition.get_data_frames()[0]
    except Exception as e:
        raise HTTPException(status_code=404, detail="Jugador no encontrado o ID inválido")
    
    if df.empty:
        raise HTTPException(status_code=404, detail="El jugador no tiene estadísticas registradas")
    
    last_season = df.iloc[-1]
    clean_data = last_season.to_dict()
    cache_players[player_id] = clean_data

    return clean_data


@app.get("/teams/{team_id}/stats", response_model=TeamSeasonStats)
def get_team_stats(team_id: int):
    if team_id in cache_teams:
        return cache_teams.get(team_id)
    
    try:
        petition = teamyearbyyearstats.TeamYearByYearStats(team_id)
        df = petition.get_data_frames()[0]
    except Exception as e:
        raise HTTPException(status_code=404, detail="Equipo no encontrado o ID inválido")
    
    if df.empty:
        raise HTTPException(status_code=404, detail="El equipo no tiene estadísticas registradas")
    
    last_season = df.iloc[-1]
    clean_data = last_season.to_dict()

    cache_teams[team_id] = clean_data

    return clean_data

@app.get("/games/{game_date}", response_model=list[GameInfo])
def get_games_by_date(game_date: date):
    today = date.today()

    if today == game_date:
        if game_date in cache_live_games:
            return cache_live_games.get(game_date)
    else:
        if game_date in cache_historical_games:
            return cache_historical_games.get(game_date)
    
    petition = scoreboardv3.ScoreboardV3(game_date=game_date)

    raw_data = petition.get_dict()

    games_list = raw_data.get("scoreboard", {}).get("games", [])

    clean_games = []

    for game in games_list:
        game_dict = {}

        game_dict["game_id"] = game["gameId"]
        game_dict["status"] = game["gameStatusText"]

        game_dict["home_team"] = {
            "id": game["homeTeam"]["teamId"],
            "name": game["homeTeam"]["teamName"],
            "score": game["homeTeam"]["score"]
        }

        game_dict["away_team"] = {
            "id": game["awayTeam"]["teamId"],
            "name": game["awayTeam"]["teamName"],
            "score": game["awayTeam"]["score"]
        }

        clean_games.append(game_dict)
    
    if today == game_date:
        cache_live_games[game_date] = clean_games
    else:
        cache_historical_games[game_date] = clean_games

    return clean_games
