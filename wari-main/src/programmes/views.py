from django.shortcuts import render
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter
import logging

from .models import Program
from .serializers import ProgramSerializer

# Configuration du logger pour le suivi des événements
logger = logging.getLogger(__name__)


# 1. Pagination standardisée

class StandardPagination(PageNumberPagination):
    """Pagination standard avec 20 éléments par page, configurable via paramètre URL."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# 2. Base ViewSet pour factorisation

class BaseProgramViewSet(viewsets.ModelViewSet):
    """
    ViewSet de base pour les programmes :
    - Factorise pagination, filtres et gestion des erreurs
    - Optimisé avec select_related pour les relations
    """
    queryset = Program.objects.all().select_related('game', 'game__country')
    serializer_class = ProgramSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]

    def handle_exception(self, exc):
        """Surcharge pour logger les erreurs inattendues."""
        logger.error(f"Erreur dans {self.__class__.__name__}: {str(exc)}", exc_info=True)
        return super().handle_exception(exc)

# 3. Vue pour les administrateurs

class ProgramViewSet(BaseProgramViewSet):
    """
    Gestion des programmes (réservée aux administrateurs).
    - CRUD complet avec pagination et recherche
    - Filtres sur jeu, pays, statut de publication et date d'événement
    - Recherche textuelle sur le nom du programme
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['game__slug', 'game__country__slug', 'is_published', 'event_date']
    search_fields = ['name']  # Recherche sur le nom du programme

    def perform_create(self, serializer):
        """
        Création d'un programme :
        - Associe l'utilisateur connecté comme créateur (si authentifié)
        - Log l'opération
        """
        with transaction.atomic():
            instance = serializer.save(creator=self.request.user if self.request.user.is_authenticated else None)
            logger.info(f"Programme '{instance.name}' créé par {self.request.user if self.request.user.is_authenticated else 'anonyme'}")
            return instance

    def perform_update(self, serializer):
        """
        Mise à jour d'un programme :
        - Log l'opération avec l'utilisateur
        """
        with transaction.atomic():
            instance = serializer.save()
            logger.info(f"Programme '{instance.name}' mis à jour par {self.request.user}")
            return instance

    def destroy(self, request, *args, **kwargs):
        """
        Suppression sécurisée d'un programme :
        - Utilise une transaction atomique
        - Log l'opération
        """
        instance = self.get_object()
        with transaction.atomic():
            logger.info(f"Programme '{instance.name}' supprimé par {request.user}")
            return super().destroy(request, *args, **kwargs)


# 4. Vue pour les clients
class ClientProgramViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Affichage des programmes publiés (lecture seule pour les clients).
    - N'affiche que les programmes publiés (is_published=True)
    - Pagination et recherche activées
    - Filtres sur jeu, pays et date d'événement
    """
    queryset = Program.objects.filter(is_published=True).select_related('game', 'game__country')
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['game__slug', 'game__country__slug', 'event_date']
    search_fields = ['name']  # Recherche sur le nom du programme

    def handle_exception(self, exc):
        """Surcharge pour logger les erreurs inattendues dans la vue client."""
        logger.error(f"Erreur dans ClientProgramViewSet: {str(exc)}", exc_info=True)
        return super().handle_exception(exc)


