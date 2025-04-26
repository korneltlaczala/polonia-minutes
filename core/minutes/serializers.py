from rest_framework import serializers

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