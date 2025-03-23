from django.shortcuts import render
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, BasePermission
from rest_framework.filters import SearchFilter
from rest_framework import serializers
import logging

from .models import Prediction
from .serializers import PredictionSerializer

# Configuration du logger pour le suivi des événements
logger = logging.getLogger(__name__)


# 1. Pagination standardisée
class StandardPagination(PageNumberPagination):
    """Pagination standard avec 20 éléments par page, configurable via paramètre URL."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# 2. Base ViewSet pour factorisation
class BasePredictionViewSet(viewsets.ModelViewSet):
    """
    ViewSet de base pour les pronostics :
    - Factorise pagination, filtres et gestion des erreurs
    - Optimisé avec select_related pour 'game' et 'author', et only() pour limiter les champs
    - Permission par défaut : lecture seule pour tous, écriture authentifiée
    """
    queryset = Prediction.objects.all().select_related('game', 'author').only(
        'id', 'game', 'author', 'is_published', 'predicted_at'
    )
    serializer_class = PredictionSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def handle_exception(self, exc):
        """Surcharge pour logger les erreurs inattendues avec contexte."""
        logger.error(f"Erreur dans {self.__class__.__name__}: {str(exc)}", exc_info=True)
        return super().handle_exception(exc)


# 3. Permission personnalisée pour admins et éditeurs
class IsAdminOrEditor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
                    request.user.is_staff or getattr(request.user, 'role', None) == 'editor')


# 4. Vue pour les administrateurs
class PredictionViewSet(BasePredictionViewSet):
    """
    Gestion des pronostics (réservée aux administrateurs et éditeurs pour CRUD complet).
    - Pagination et recherche activées
    - Filtres : slug du jeu, nom d'utilisateur, statut de publication, date de prédiction
    - Recherche : nom du jeu
    """
    permission_classes = [IsAdminOrEditor]
    filterset_fields = ['game__slug', 'author__username', 'is_published', 'predicted_at']
    search_fields = ['game__name']

    def perform_create(self, serializer):
        """Création d'un pronostic avec l'utilisateur connecté comme auteur."""
        if not self.request.user.is_authenticated:
            raise serializers.ValidationError("Authentification requise pour créer un pronostic.")
        with transaction.atomic():
            instance = serializer.save(author=self.request.user)
            logger.info(f"Pronostic créé pour '{instance.game.name}' par {self.request.user.username}")
            return instance

    def perform_update(self, serializer):
        """Mise à jour d'un pronostic, réservée à l'auteur ou aux admins."""
        instance = self.get_object()
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise serializers.ValidationError("Seul l'auteur ou un admin peut modifier ce pronostic.")
        with transaction.atomic():
            updated_instance = serializer.save()
            logger.info(f"Pronostic mis à jour pour '{updated_instance.game.name}' par {self.request.user.username}")
            return updated_instance

    def destroy(self, request, *args, **kwargs):
        """Suppression d'un pronostic, réservée à l'auteur ou aux admins."""
        instance = self.get_object()
        if instance.author != request.user and not request.user.is_staff:
            return Response(
                {"detail": "Seul l'auteur ou un admin peut supprimer ce pronostic."},
                status=status.HTTP_403_FORBIDDEN
            )
        with transaction.atomic():
            logger.info(f"Pronostic supprimé pour '{instance.game.name}' par {request.user.username}")
            return super().destroy(request, *args, **kwargs)


# 5. Vue pour les clients (lecture seule)
class ClientPredictionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Affichage des pronostics publiés (lecture seule) :
    - Restreint aux pronostics publiés (is_published=True)
    - Pagination et recherche activées
    - Filtres : slug du jeu, date de prédiction
    - Recherche : nom du jeu
    """
    queryset = Prediction.objects.filter(is_published=True).select_related('game', 'author').only(
        'id', 'game', 'author', 'predicted_at'
    )
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['game__slug', 'predicted_at']
    search_fields = ['game__name']

    def handle_exception(self, exc):
        """Surcharge pour logger les erreurs inattendues dans la vue client."""
        logger.error(f"Erreur dans ClientPredictionViewSet: {str(exc)}", exc_info=True)
        return super().handle_exception(exc)
