from rest_framework import serializers
from .models import Result

class ResultSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les résultats, inclut les relations avec jeu et validateur."""
    game = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    validated_by = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Result
        fields = ['id', 'game', 'result_date', 'outcome', 'outcome_details', 'status', 'validated_by', 'created_at']
        read_only_fields = ['created_at', 'validated_by']

    def validate(self, data):
        """Vérifie la cohérence entre status et validated_by."""
        if data.get('status') == 'official' and not self.context['request'].user.is_authenticated:
            raise serializers.ValidationError("Un résultat officiel doit être validé par un utilisateur.")
        return data

    def validate_outcome(self, value):
        """Vérifie que le champ outcome n'est pas vide."""
        if not value.strip():
            raise serializers.ValidationError("Le résultat ne peut pas être vide.")
        return value