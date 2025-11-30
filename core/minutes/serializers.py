from rest_framework import serializers
from datetime import datetime

class MatchSerializer(serializers.Serializer):
    league_name = serializers.CharField(source="league.name")
    score = serializers.CharField(source="scores.final")

    # host_logo_url = serializers.CharField(source="host.logo")
    # guest_logo_url = serializers.CharField(source="guest.logo")
    host_logo_url = serializers.SerializerMethodField()
    guest_logo_url = serializers.SerializerMethodField()
    FALLBACK_LOGO_URL = "https://www.laczynaspilka.pl/rozgrywki/assets/icons/crest_default.svg"

    host_name = serializers.CharField(source="host.name")
    guest_name = serializers.CharField(source="guest.name")
    host_abbreviation = serializers.CharField(source="host.abbreviation")
    guest_abbreviation = serializers.CharField(source="guest.abbreviation")
    is_home_match = serializers.BooleanField()

    def get_host_logo_url(self, obj):
        try:
            return obj.host["logo"]
        except (KeyError, TypeError):
            return self.FALLBACK_LOGO_URL

    def get_guest_logo_url(self, obj):
        try:
            return obj.guest["logo"]
        except (KeyError, TypeError):
            return self.FALLBACK_LOGO_URL

    date = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    month = serializers.SerializerMethodField()
    day = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    def get_date(self, obj):
        dt = datetime.fromisoformat(obj.dateTime)
        return dt.date().isoformat()

    def get_time(self, obj):
        dt = datetime.fromisoformat(obj.dateTime)
        return dt.time().isoformat()

    def get_year(self, obj):
        dt = datetime.fromisoformat(obj.dateTime)
        return dt.year

    def get_month(self, obj):
        dt = datetime.fromisoformat(obj.dateTime)
        return dt.month

    def get_day(self, obj):
        dt = datetime.fromisoformat(obj.dateTime)
        return dt.day


class AppearanceSerializer(serializers.Serializer):
    match = MatchSerializer()
    duration = serializers.IntegerField()
    minute_in = serializers.IntegerField()
    minute_out = serializers.IntegerField()
    goal_count = serializers.IntegerField()
    yellow_card_count = serializers.IntegerField()
    played = serializers.BooleanField()
    
class PlayerSerializer(serializers.Serializer):
    id = serializers.CharField()
    firstname = serializers.CharField()
    lastname = serializers.CharField()
    minutes = serializers.IntegerField()
    minutes_per_game = serializers.IntegerField()
    apps = serializers.IntegerField()
    callings = serializers.IntegerField()
    appearances = AppearanceSerializer(many=True)
    goal_count = serializers.IntegerField()
    goals_per_90 = serializers.FloatField()
    goals_per_game = serializers.FloatField()
    yellow_cards = serializers.IntegerField()

    def get_name(self, obj):
        return f"{obj.firstname} {obj.lastname}"

