from network_capture import Sniffer
from objects import Team
import json

with open ("sources/teams.json", "r", encoding="utf-8") as f:
    teams = json.load(f)

sniffer = Sniffer()
for team in teams:
    team = Team(team["teamName"], team["teamFolder"], team["teamUrl"])
    sniffer.capture(team)
    sniffer.destroy()