from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResultViewSet, ClientResultViewSet

# Routeur pour les endpoints admin (CRUD complet)
admin_router = DefaultRouter()
admin_router.register(r'results', ResultViewSet, basename='admin-result')

# Routeur pour les endpoints client (lecture seule)
client_router = DefaultRouter()
client_router.register(r'results', ClientResultViewSet, basename='client-result')

# URLs différenciées pour admin et client
urlpatterns = [
    path('admin/', include(admin_router.urls)),  # /api/admin/results/
    path('client/', include(client_router.urls)),  # /api/client/results/
]