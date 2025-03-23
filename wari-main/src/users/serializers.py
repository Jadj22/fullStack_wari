from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les utilisateurs, utilisé par les admins."""
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'is_active', 'date_joined']
        read_only_fields = ['date_joined']

    def validate_role(self, value):
        """Valide que le rôle est parmi les choix autorisés."""
        if value not in dict(CustomUser.ROLE_CHOICES).keys():
            raise serializers.ValidationError("Rôle invalide.")
        return value