from rest_framework import serializers

class ApearanceSerializer(serializers.Serializer):
    match = serializers.CharField(source="match.__str__")
    duration = serializers.IntegerField()
    minute_in = serializers.IntegerField()
    minute_out = serializers.IntegerField()

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