from rest_framework import serializers
from datetime import datetime

class ApearanceSerializer(serializers.Serializer):
    match = serializers.CharField(source="match.__str__")
    duration = serializers.IntegerField()
    minute_in = serializers.IntegerField()
    minute_out = serializers.IntegerField()
    score = serializers.CharField(source="match.scores.final")
    host_logo_url = serializers.CharField(source="match.host.logo")
    guest_logo_url = serializers.CharField(source="match.guest.logo")
    host_name = serializers.CharField(source="match.host.name")
    guest_name = serializers.CharField(source="match.guest.name")
    host_abbreviation = serializers.CharField(source="match.host.abbreviation")
    guest_abbreviation = serializers.CharField(source="match.guest.abbreviation")
    date = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    month = serializers.SerializerMethodField()
    day = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    def get_date(self, obj):
        dt = datetime.fromisoformat(obj.match.dateTime)
        return dt.date().isoformat()

    def get_time(self, obj):
        dt = datetime.fromisoformat(obj.match.dateTime)
        return dt.time().isoformat()

    def get_year(self, obj):
        dt = datetime.fromisoformat(obj.match.dateTime)
        return dt.year

    def get_month(self, obj):
        dt = datetime.fromisoformat(obj.match.dateTime)
        return dt.month

    def get_day(self, obj):
        dt = datetime.fromisoformat(obj.match.dateTime)
        return dt.day
    



class PlayerSerializer(serializers.Serializer):
    id = serializers.CharField()
    firstname = serializers.CharField()
    lastname = serializers.CharField()
    minutes = serializers.IntegerField()
    apps = serializers.IntegerField()
    callings = serializers.IntegerField()
    appearances = ApearanceSerializer(many=True)

    def get_name(self, obj):
        return f"{obj.firstname} {obj.lastname}"