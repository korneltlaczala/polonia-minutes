from django.shortcuts import render
from .serializers import PlayerSerializer, MatchSerializer
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

@api_view(['GET'])
def team_players_api(request):
    team_id = request.GET.get('team_id')
    active_leagues_raw = request.GET.get('active_leagues', '').strip()
    active_leagues = active_leagues_raw.split(',') if active_leagues_raw else []
    if not team_id:
        return Response({"error": "No team provided"}, status=400)

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
    