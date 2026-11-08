from rest_framework import serializers
from .models import Business


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['id', 'name', 'description', 'base_price', 'income_per_second']


class PurchaseSerializer(serializers.Serializer):
    quantity = serializers.ChoiceField(choices=['1', '10', 'max'], default='1')

    def validate_quantity(self, value):

        if not isinstance(self.initial_data.get('quantity', '1'), str):
            raise serializers.ValidationError('Choose 1, 10, or max as a string.')
        return value


class PrestigeSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if self.initial_data.get('confirm') is not True:
            raise serializers.ValidationError('Confirm the prestige reset before continuing.')
        return value


class GameStateSerializer(serializers.Serializer):

    username = serializers.CharField()
    money = serializers.CharField()
    lifetime_earnings = serializers.CharField()
    last_income_at = serializers.CharField()
    prestige_count = serializers.IntegerField()
    achievement_points = serializers.IntegerField()
    income_per_second = serializers.CharField()
    income_multiplier = serializers.CharField()
    income_earned = serializers.CharField(required=False)
    businesses = serializers.ListField(child=serializers.DictField())
    achievements = serializers.ListField(child=serializers.DictField())
    global_upgrades = serializers.ListField(child=serializers.DictField())
    daily_reward = serializers.DictField()
    prestige = serializers.DictField()
    statistics = serializers.DictField()
