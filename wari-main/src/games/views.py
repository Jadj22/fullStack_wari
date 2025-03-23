from django.shortcuts import render
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import BasePermission
from rest_framework.filters import SearchFilter
import logging

from .models import Country, GameType, Game
from .serializers import CountrySerializer, GameTypeSerializer, GameSerializer

# Configuration du logger pour le suivi des événements
logger = logging.getLogger(__name__)


# 1. Pagination standardisée

class StandardPagination(PageNumberPagination):
    """Pagination standard avec 20 éléments par page, configurable via paramètre URL."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# 2. Permission personnalisée

class IsAdminOrReadOnly(BasePermission):
    """
    Permission personnalisée :
    - Lecture seule pour tous les utilisateurs
    - Écriture (POST, PUT, DELETE) réservée aux administrateurs
    """
    def has_permission(self, request, view):
        return request.method in ["GET", "HEAD", "OPTIONS"] or request.user.is_staff


# 3. Base ViewSet pour factorisation

class BaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet de base factorisant les configurations communes :
    - Permissions : admin pour écriture, lecture pour tous
    - Pagination : 20 éléments par page
    - Filtres : DjangoFilterBackend et SearchFilter
    """
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]

    def handle_exception(self, exc):
        """Surcharge pour logger les erreurs inattendues."""
        logger.error(f"Erreur dans {self.__class__.__name__}: {str(exc)}", exc_info=True)
        return super().handle_exception(exc)


# 4. ViewSet pour les Pays

class CountryViewSet(BaseViewSet):
    """
    Gestion des pays (CRUD complet pour admins, lecture pour tous).
    - Optimisation avec prefetch_related et champs spécifiques via only()
    - Filtres et recherche sur nom, code, slug
    """
    queryset = Country.objects.all().prefetch_related('games').only('id', 'name', 'code', 'slug')
    serializer_class = CountrySerializer
    filterset_fields = ['name', 'code', 'slug']
    search_fields = ['name', 'code']

    def destroy(self, request, *args, **kwargs):
        """
        Suppression sécurisée d'un pays :
        - Vérifie l'absence de jeux associés
        - Utilise une transaction atomique
        - Log les tentatives échouées
        """
        instance = self.get_object()
        if instance.games.exists():
            logger.warning(f"Tentative de suppression du pays '{instance.name}' avec jeux associés")
            return Response(
                {"detail": "Impossible de supprimer ce pays : des jeux y sont associés."},
                status=status.HTTP_400_BAD_REQUEST
            )
        with transaction.atomic():
            logger.info(f"Suppression réussie du pays '{instance.name}'")
            return super().destroy(request, *args, **kwargs)


# 5. ViewSet pour les Types de Jeu
class GameTypeViewSet(BaseViewSet):
    """
    Gestion des types de jeux (CRUD complet pour admins, lecture pour tous).
    - Optimisation avec prefetch_related et champs spécifiques via only()
    - Filtres et recherche sur nom, slug
    """
    queryset = GameType.objects.all().prefetch_related('games').only('id', 'name', 'slug')
    serializer_class = GameTypeSerializer
    filterset_fields = ['name', 'slug']
    search_fields = ['name']

    def destroy(self, request, *args, **kwargs):
        """
        Suppression sécurisée d'un type de jeu :
        - Vérifie l'absence de jeux associés
        - Utilise une transaction atomique
        - Log les tentatives échouées
        """
        instance = self.get_object()
        if instance.games.exists():
            logger.warning(f"Tentative de suppression du type '{instance.name}' avec jeux associés")
            return Response(
                {"detail": "Impossible de supprimer ce type : des jeux y sont associés."},
                status=status.HTTP_400_BAD_REQUEST
            )
        with transaction.atomic():
            logger.info(f"Suppression réussie du type '{instance.name}'")
            return super().destroy(request, *args, **kwargs)


# 6. ViewSet pour les Jeux
class GameViewSet(BaseViewSet):
    """
    Gestion des jeux (CRUD complet pour admins, lecture pour tous).
    - Optimisation avec select_related et champs spécifiques via only()
    - Filtres et recherche sur nom, description, pays, type, statut
    """
    queryset = Game.objects.all().select_related('country', 'game_type').only(
        'id', 'name', 'description', 'country', 'game_type', 'is_active'
    )
    serializer_class = GameSerializer
    filterset_fields = ['country__slug', 'game_type__slug', 'is_active', 'name']
    search_fields = ['name', 'description']

    def perform_create(self, serializer):
        """
        Création d'un jeu avec logging.
        - Peut être étendu pour des validations spécifiques
        """
        instance = serializer.save()
        logger.info(f"Jeu '{instance.name}' créé avec succès")

    def perform_update(self, serializer):
        """
        Mise à jour d'un jeu avec logging.
        """
        instance = serializer.save()
        logger.info(f"Jeu '{instance.name}' mis à jour avec succès")


 #7. ViewSet en lecture seule pour les Clients
class ClientGameViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Affichage des jeux actifs pour les clients (lecture seule).
    - Optimisation avec select_related et champs spécifiques via only()
    - Filtres et recherche sur nom, description, pays, type
    """
    queryset = Game.objects.filter(is_active=True).select_related('country', 'game_type').only(
        'id', 'name', 'description', 'country', 'game_type'
    )
    serializer_class = GameSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['country__slug', 'game_type__slug']
    search_fields = ['name', 'description']