import os
from django.shortcuts import render
from .serializers import PlayerSerializer, MatchSerializer, AppearanceSerializer
from mincal import Club

from rest_framework.response import Response
from rest_framework.decorators import api_view

CLUBS_CACHE = {}
DEFAULT_SEASON = "2026-2027"

def get_available_seasons():
    seasons_dir = os.path.normpath(os.path.join("data", "polonia", "seasons"))
    if os.path.exists(seasons_dir):
        seasons = [d for d in os.listdir(seasons_dir) if os.path.isdir(os.path.join(seasons_dir, d))]
        seasons.sort(reverse=True)
        return seasons
    return [DEFAULT_SEASON]

def get_requested_season(request):
    available_seasons = get_available_seasons()
    season = request.GET.get('season')
    if season and season in available_seasons:
        request.session['season'] = season
        return season
    
    session_season = request.session.get('season')
    if session_season and session_season in available_seasons:
        return session_season
        
    return DEFAULT_SEASON

def get_club(season):
    if season not in CLUBS_CACHE:
        folder = f"polonia/seasons/{season}"
        club_obj = Club("Polonia Warszawa", folder)
        club_obj.prep_stats()
        CLUBS_CACHE[season] = club_obj
    return CLUBS_CACHE[season]

def get_common_context(request):
    season = get_requested_season(request)
    club = get_club(season)
    available_seasons = get_available_seasons()
    return {
        "club": club,
        "current_season": season,
        "available_seasons": available_seasons,
    }

def choose_team(request):
    context = get_common_context(request)
    return render(request, 'choose_team.html', context)

def team(request, team_id):
    context = get_common_context(request)
    team_obj = context["club"].get_team(team_id)
    context["team"] = team_obj
    return render(request, 'team.html', context)

def team_minutes(request, team_id):
    context = get_common_context(request)
    team_obj = context["club"].get_team(team_id)
    context["team"] = team_obj
    return render(request, 'team_minutes.html', context)

def team_matches(request, team_id):
    context = get_common_context(request)
    team_obj = context["club"].get_team(team_id)
    context["team"] = team_obj
    return render(request, 'team_matches.html', context)

def player(request, player_id):
    context = get_common_context(request)
    player_obj = context["club"].get_player(player_id)
    context["player"] = player_obj
    return render(request, 'player.html', context)

@api_view(['GET'])
def team_players_api(request):
    team_id = request.GET.get('team_id')
    active_leagues_raw = request.GET.get('active_leagues', '').strip()
    active_leagues = active_leagues_raw.split(',') if active_leagues_raw else []
    if not team_id:
        return Response({"error": "No team provided"}, status=400)

    season = get_requested_season(request)
    club = get_club(season)
    players = club.get_players_for_team(team_id, active_leagues)
    serializer = PlayerSerializer(players, many=True)
    return Response({"players": serializer.data})

@api_view(['GET'])
def team_matches_api(request):
    team_id = request.GET.get('team_id')
    active_leagues = request.GET.get('active_leagues', '').strip()
    active_leagues = active_leagues.split(',') if active_leagues else []
    if not team_id:
        return Response({"error": "No team provided"}, status=400)

    season = get_requested_season(request)
    club = get_club(season)
    played_matches, not_played_matches = club.get_matches_for_team(team_id, active_leagues)
    serializer_played = MatchSerializer(played_matches, many=True)
    serializer_not_played = MatchSerializer(not_played_matches, many=True)
    return Response({"played_matches": serializer_played.data, "not_played_matches": serializer_not_played.data})
    
@api_view(['GET'])
def player_matches_api(request):
    player_id = request.GET.get('player_id')
    active_leagues_raw = request.GET.get('active_leagues', '').strip()
    active_leagues = active_leagues_raw.split(',') if active_leagues_raw else []
    if not player_id:
        return Response({"error": "No player provided"}, status=400)

    season = get_requested_season(request)
    club = get_club(season)
    appearances = club.get_appearances_for_player(player_id, active_leagues)
    serializer = AppearanceSerializer(appearances, many=True)
    return Response({"appearances": serializer.data})