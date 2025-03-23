from django.shortcuts import render
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter
import logging

from .models import Result
from .serializers import ResultSerializer

# Configuration du logger pour le suivi des événements
logger = logging.getLogger(__name__)


# 1. Pagination standardisée
class StandardPagination(PageNumberPagination):
    """Pagination standard avec 20 éléments par page, configurable via paramètre URL."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# 2. Base ViewSet pour factorisation

class BaseResultViewSet(viewsets.ModelViewSet):
    """
    ViewSet de base pour les résultats :
    - Factorise pagination, filtres et gestion des erreurs
    - Optimisé avec select_related pour 'game' et 'validated_by', et prefetch_related pour 'game__country'
    """
    queryset = Result.objects.all().select_related('game', 'validated_by').prefetch_related('game__country')
    serializer_class = ResultSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    permission_classes = [IsAuthenticatedOrReadOnly]  # Par défaut, lecture seule

    def handle_exception(self, exc):
        """Surcharge pour logger les erreurs inattendues."""
        logger.error(f"Erreur dans {self.__class__.__name__}: {str(exc)}", exc_info=True)
        return super().handle_exception(exc)

# 3. Vue pour les administrateurs
class ResultViewSet(BaseResultViewSet):
    """
    Gestion des résultats (réservée aux administrateurs).
    - CRUD complet avec pagination et recherche
    - Filtres : slug du jeu, slug du pays, statut, date de résultat
    - Recherche : nom du jeu
    """
    permission_classes = [IsAdminUser]
    filterset_fields = ['game__slug', 'game__country__slug', 'status', 'result_date']
    search_fields = ['game__name']  # Recherche sur le nom du jeu

    def perform_create(self, serializer):
        """
        Création d'un résultat :
        - Associe validated_by si status='official' et utilisateur authentifié
        - Transaction atomique et logging
        """
        with transaction.atomic():
            status_value = serializer.validated_data.get('status')
            validated_by = self.request.user if status_value == 'official' and self.request.user.is_authenticated else None
            instance = serializer.save(validated_by=validated_by)
            logger.info(f"Résultat créé pour '{instance.game.name}' (status: {status_value}) par {self.request.user.username}")
            return instance

    def perform_update(self, serializer):
        """
        Mise à jour d'un résultat :
        - Met à jour validated_by si status passe à 'official'
        - Transaction atomique et logging
        """
        with transaction.atomic():
            status_value = serializer.validated_data.get('status')
            if status_value == 'official' and self.request.user.is_authenticated:
                instance = serializer.save(validated_by=self.request.user)
                logger.info(f"Résultat officialisé pour '{instance.game.name}' par {self.request.user.username}")
            else:
                instance = serializer.save()
                logger.info(f"Résultat mis à jour pour '{instance.game.name}' par {self.request.user.username}")
            return instance

    def destroy(self, request, *args, **kwargs):
        """
        Suppression d'un résultat :
        - Réservé aux admins
        - Transaction atomique et logging
        """
        instance = self.get_object()
        with transaction.atomic():
            logger.info(f"Résultat supprimé pour '{instance.game.name}' par {request.user.username}")
            return super().destroy(request, *args, **kwargs)


# 4. Vue pour les clients (lecture seule)

class ClientResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Affichage des résultats officiels ou contestés (lecture seule) :
    - Restreint à status='official' ou 'disputed'
    - Pagination et recherche activées
    - Filtres : slug du jeu, statut, date de résultat
    - Recherche : nom du jeu
    """
    queryset = Result.objects.filter(status__in=['official', 'disputed']).select_related('game', 'validated_by').prefetch_related('game__country')
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['game__slug', 'status', 'result_date']
    search_fields = ['game__name']  # Recherche sur le nom du jeu

    def handle_exception(self, exc):
        """Surcharge pour logger les erreurs inattendues dans la vue client."""
        logger.error(f"Erreur dans ClientResultViewSet: {str(exc)}", exc_info=True)
        return super().handle_exception(exc)

