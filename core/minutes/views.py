from django.shortcuts import render
from .serializers import PlayerSerializer, MatchSerializer, AppearanceSerializer
from mincal import Club

from rest_framework.response import Response
from rest_framework.decorators import api_view

# Create your views here.
club = Club("Polonia Warszawa", "polonia")
club.prep_stats()

def choose_team(request):
    context = {"club": club}
    return render(request, 'choose_team.html', context)

def team(request, team_id):
    team = club.get_team(team_id)
    context = {"club": club,
               "team": team}
    return render(request, 'team.html', context)

def team_minutes(request, team_id):
    team = club.get_team(team_id)
    context = {"club": club,
               "team": team}
    return render(request, 'team_minutes.html', context)

def team_matches(request, team_id):
    team = club.get_team(team_id)
    context = {"club": club,
               "team": team}
    return render(request, 'team_matches.html', context)

def player(request, player_id):
    player = club.get_player(player_id)
    context = {"club": club,
               "player": player}
    return render(request, 'player.html', context)

@api_view(['GET'])
def team_players_api(request):
    team_id = request.GET.get('team_id')
    active_leagues_raw = request.GET.get('active_leagues', '').strip()
    active_leagues = active_leagues_raw.split(',') if active_leagues_raw else []
    if not team_id:
        return Response({"error": "No team provided"}, status=400)

    print(f"Getting players for team: {team_id}")
    print(f"Active leagues: {active_leagues}")
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

    print(f"Getting matches for player: {player_id}")
    print(f"Active leagues: {active_leagues}")
    appearances = club.get_appearances_for_player(player_id, active_leagues)
    serializer = AppearanceSerializer(appearances, many=True)
    return Response({"appearances": serializer.data})