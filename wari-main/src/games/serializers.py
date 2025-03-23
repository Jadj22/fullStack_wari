from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Country, GameType, Game

class CountrySerializer(serializers.ModelSerializer):
    """Sérialiseur pour les pays, inclut le nombre de jeux associés."""
    game_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Country
        fields = ['id', 'name', 'code', 'slug', 'game_count', 'created_at']
        read_only_fields = ['slug', 'created_at']

    def get_game_count(self, obj):
        """Calcule le nombre de jeux associés au pays."""
        # Note : Utiliser prefetch_related dans la vue pour optimiser
        return obj.games.count()

    def validate_code(self, value):
        """Vérifie que le code est un code ISO alpha-3 valide (3 caractères)."""
        if len(value) != 3:
            raise serializers.ValidationError("Le code pays doit contenir exactement 3 caractères (ISO alpha-3).")
        return value.upper()

    def validate_name(self, value):
        """Vérifie que le nom n'est pas vide."""
        if not value.strip():
            raise serializers.ValidationError("Le nom du pays ne peut pas être vide.")
        return value

class GameTypeSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les types de jeux, inclut le nombre de jeux associés."""
    game_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GameType
        fields = ['id', 'name', 'slug', 'game_count', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_game_count(self, obj):
        """Calcule le nombre de jeux associés au type."""
        # Note : Utiliser prefetch_related dans la vue pour optimiser
        return obj.games.count()

    def validate_name(self, value):
        """Vérifie que le nom n'est pas vide."""
        if not value.strip():
            raise serializers.ValidationError("Le nom du type de jeu ne peut pas être vide.")
        return value

class GameSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les jeux, inclut les relations avec pays et type de jeu."""
    country = CountrySerializer(read_only=True)
    game_type = GameTypeSerializer(read_only=True)
    # Champs pour l'entrée (écriture) des relations
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        source='country',
        write_only=True,
        required=True
    )
    game_type_id = serializers.PrimaryKeyRelatedField(
        queryset=GameType.objects.all(),
        source='game_type',
        write_only=True,
        required=True
    )

    class Meta:
        model = Game
        fields = [
            'id', 'name', 'slug', 'game_type', 'game_type_id',
            'country', 'country_id', 'is_active', 'created_at', 'description', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def validate_name(self, value):
        """Vérifie que le nom respecte les contraintes du modèle."""
        if not value.strip():
            raise serializers.ValidationError("Le nom du jeu ne peut pas être vide.")
        if len(value) < 3:
            raise serializers.ValidationError("Le nom du jeu doit comporter au moins 3 caractères.")
        return value

    def validate(self, data):
        """Vérifie que le nom du jeu est unique par pays, pour la création et la mise à jour."""
        country = data.get('country')  # L'objet Country résolu à partir de country_id
        name = data.get('name')

        if not country:
            raise serializers.ValidationError({"country_id": "Le pays est obligatoire."})
        if not data.get('game_type'):
            raise serializers.ValidationError({"game_type_id": "Le type de jeu est obligatoire."})

        # Vérification de l'unicité
        existing_game = Game.objects.filter(name=name, country=country)
        if self.instance:  # Mise à jour
            existing_game = existing_game.exclude(id=self.instance.id)
        if existing_game.exists():
            raise serializers.ValidationError(
                "Un jeu avec ce nom existe déjà pour ce pays."
            )

        return data