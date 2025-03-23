from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProgramViewSet, ClientProgramViewSet

# Routeur pour les endpoints admin
admin_router = DefaultRouter()
admin_router.register(r'programs', ProgramViewSet, basename='admin-program')

# Routeur pour les endpoints client
client_router = DefaultRouter()
client_router.register(r'programs', ClientProgramViewSet, basename='client-program')

# URLs différenciées
urlpatterns = [
    path('', include(admin_router.urls)),  # /api/admin/programs/
    path('', include(client_router.urls)),  # /api/client/programs/
]