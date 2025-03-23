from rest_framework import serializers
from django.utils import timezone
from .models import Program

class ProgramSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les programmes :
    - Inclut le slug du jeu via SlugRelatedField
    - Valide les champs clés (event_date, details)
    - Champs en lecture seule protégés
    """
    game = serializers.SlugRelatedField(
        slug_field='slug',
        read_only=True,
        help_text="Slug du jeu associé au programme."
    )

    class Meta:
        model = Program
        fields = ['id', 'game', 'event_date', 'details', 'is_published', 'created_at']
        read_only_fields = ['created_at']
        extra_kwargs = {
            'event_date': {'required': True, 'help_text': "Date de l'événement (non passée)."},
            'details': {'required': True, 'help_text': "Détails du programme (non vides)."},
            'is_published': {'default': False, 'help_text': "Statut de publication du programme."},
        }

    def validate_event_date(self, value):
        """
        Valide la date de l'événement :
        - Doit être dans le futur ou aujourd'hui
        - Lève une exception si la date est dans le passé
        """
        now = timezone.now()
        if value < now:
            raise serializers.ValidationError(
                f"La date de l'événement ({value}) ne peut pas être antérieure à maintenant ({now})."
            )
        return value

    def validate_details(self, value):
        """
        Valide les détails :
        - Ne doit pas être vide ou ne contenir que des espaces
        - Minimum 10 caractères pour garantir un contenu significatif
        """
        cleaned_value = value.strip()
        if not cleaned_value:
            raise serializers.ValidationError("Les détails ne peuvent pas être vides.")
        if len(cleaned_value) < 10:
            raise serializers.ValidationError("Les détails doivent contenir au moins 10 caractères.")
        return cleaned_value

    def validate(self, attrs):
        """
        Validation globale :
        - Peut être utilisé pour des vérifications interdépendantes si nécessaire
        """
        return attrs

    def to_representation(self, instance):
        """
        Personnalisation de la représentation :
        - Ajoute le nom du jeu en plus du slug pour les clients (optionnel)
        """
        representation = super().to_representation(instance)
        if instance.game:
            representation['game_name'] = instance.game.name  # Ajoute le nom du jeu
        return representation