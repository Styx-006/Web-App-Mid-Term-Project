from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        read_only_fields = ['id']

    def validate(self, data):
        user = User(username=data['username'])
        try:
            validate_password(data['password'], user=user)
        except ValidationError as error:
            raise serializers.ValidationError({'password': error.messages})
        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
