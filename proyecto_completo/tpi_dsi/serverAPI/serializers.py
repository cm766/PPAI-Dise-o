from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Usuario, Bolsin

class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
class UsuarioSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer()
    class Meta:
        model = Usuario
        fields = ['user','empleado']

class BolsinSerializer(serializers.ModelSerializer):
    destino = serializers.StringRelatedField()
    origen = serializers.StringRelatedField()

    class Meta:
        model = Bolsin
        fields = [
          "fecha",
          "numeroBolsin",
          "numeroPrecinto",
          "peso",
          "destino",
          "origen",
          "cambioEstado"
        ] 