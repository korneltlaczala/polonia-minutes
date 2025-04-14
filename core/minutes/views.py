from django.shortcuts import render
from mincal import Club

# Create your views here.
club = Club("Polonia Warszawa", "polonia")
club.prep_stats()

def choose_team(request):
    context = {"club": club}
    return render(request, 'choose_team.html', context)

def player_list(request):
    context = {"club": club}
    return render(request, 'player_list.html', context)