from sniffer import Sniffer
from objects import Team
import json

with open ("sources/teams.json", "r", encoding="utf-8") as f:
    teams = json.load(f)

for team in teams:
    sniffer = Sniffer(base_dir="test")
    team = Team(team["teamName"], team["teamFolder"], team["teamUrl"])
    sniffer.capture(team)
    sniffer.destroy()