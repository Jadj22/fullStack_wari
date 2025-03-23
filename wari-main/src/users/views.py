from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import CustomUser
from .serializers import CustomUserSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    """API pour gérer les utilisateurs (réservée aux admins)."""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUser]  # Seuls les admins peuvent accéder
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['username', 'email', 'role', 'is_active']

    def perform_destroy(self, instance):
        """Empêche la suppression de l'utilisateur connecté."""
        if instance == self.request.user:
            raise serializers.ValidationError("Vous ne pouvez pas supprimer votre propre compte.")
        instance.delete()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Retourne les informations de l'utilisateur connecté."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
