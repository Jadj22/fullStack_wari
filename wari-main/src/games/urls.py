from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CountryViewSet, GameTypeViewSet, GameViewSet, ClientGameViewSet

# Routeur pour les endpoints admin (CRUD complet)
admin_router = DefaultRouter()
admin_router.register(r'countries', CountryViewSet, basename='admin-country')
admin_router.register(r'game-types', GameTypeViewSet, basename='admin-gametype')
admin_router.register(r'games', GameViewSet, basename='admin-game')

# Routeur pour les endpoints client (lecture seule, données filtrées)
client_router = DefaultRouter()
client_router.register(r'games', ClientGameViewSet, basename='client-game')

# URLs différenciées pour admin et client
urlpatterns = [
    path('', include(admin_router.urls)),  # /api/admin/games/
    path('', include(client_router.urls)),  # /api/client/games/
]