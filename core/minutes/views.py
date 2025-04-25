from django.shortcuts import render
from .serializers import PlayerSerializer
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

@api_view(['GET'])
def team_players_api(request):
    team_id = request.GET.get('team_id')
    if not team_id:
        return Response({"error": "No team provided"}, status=400)

    players = club.get_players_for_team(team_id)
    serializer = PlayerSerializer(players, many=True)
    return Response({"players": serializer.data})
