from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PredictionViewSet, ClientPredictionViewSet

# Routeur pour les endpoints admin (CRUD complet)
admin_router = DefaultRouter()
admin_router.register(r'predictions', PredictionViewSet, basename='admin-prediction')

# Routeur pour les endpoints client (lecture seule)
client_router = DefaultRouter()
client_router.register(r'predictions', ClientPredictionViewSet, basename='client-prediction')

# URLs différenciées pour admin et client
urlpatterns = [
    path('admin/', include(admin_router.urls)),  # /api/admin/predictions/
    path('client/', include(client_router.urls)),  # /api/client/predictions/
]