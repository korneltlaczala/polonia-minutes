"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.choose_team, name='choose_team'),
    path('team/<int:team_id>', views.team, name='team'),
    path('team/<int:team_id>/minutes', views.team_minutes, name='team_minutes'),
    path('team/<int:team_id>/matches', views.team_matches, name='team_matches'),

    path('player/<str:player_id>', views.player, name='player'),

    path('api/team-players/', views.team_players_api, name='team_players_api'),
    path('api/team-matches/', views.team_matches_api, name='team_matches_api'),
    path('api/player-matches/', views.player_matches_api, name='player_matches_api'),
]
