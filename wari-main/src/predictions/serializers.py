from rest_framework import serializers
from django.utils import timezone
from .models import Prediction
from games.models import Game  # Importation absolue

class PredictionSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les pronostics :
    - Inclut les relations avec jeu (slug) et auteur (username)
    - Valide les champs modifiables (description)
    - Champs en lecture seule protégés
    """
    game = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Game.objects.all(),  # Permet l'écriture par slug
        help_text="Slug du jeu associé au pronostic."
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        help_text="Nom d'utilisateur de l'auteur du pronostic."
    )

    class Meta:
        model = Prediction
        fields = ['id', 'game', 'description', 'predicted_at', 'is_published', 'author', 'updated_at']
        read_only_fields = ['predicted_at', 'updated_at', 'author']
        extra_kwargs = {
            'description': {'required': True, 'help_text': "Description du pronostic (non vide)."},
            'is_published': {'default': False, 'help_text': "Statut de publication du pronostic."},
        }

    def validate_description(self, value):
        """
        Valide la description :
        - Ne doit pas être vide ou ne contenir que des espaces
        - Minimum 15 caractères pour un contenu significatif
        """
        cleaned_value = value.strip()
        if not cleaned_value:
            raise serializers.ValidationError("La description ne peut pas être vide.")
        if len(cleaned_value) < 15:
            raise serializers.ValidationError("La description doit contenir au moins 15 caractères.")
        return cleaned_value

    def validate(self, attrs):
        """
        Validation globale :
        - Vérifie que predicted_at est défini correctement lors de la création (si nécessaire)
        """
        if self.instance is None:  # Création
            attrs['predicted_at'] = timezone.now()  # Définit automatiquement predicted_at
        return attrs

    def to_representation(self, instance):
        """
        Personnalisation de la représentation :
        - Ajoute le nom du jeu et des détails supplémentaires pour les clients
        """
        representation = super().to_representation(instance)
        if instance.game:
            representation['game_name'] = instance.game.name  # Nom du jeu en plus du slug
        if instance.author:
            representation['author_display'] = instance.author.get_full_name() or instance.author.username
        return representation