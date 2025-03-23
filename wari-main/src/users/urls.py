from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet

# Routeur pour les endpoints admin (CRUD complet, réservé aux admins)
admin_router = DefaultRouter()
admin_router.register(r'users', CustomUserViewSet, basename='admin-user')

# Pas d'endpoint client pour les utilisateurs (données sensibles)
urlpatterns = [
    path('', include(admin_router.urls)),  # /api/admin/users/
]