from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('api/admin/', include([
        path('', include('games.urls')),
        path('', include('programmes.urls')),
        path('', include('predictions.urls')),
        path('', include('results.urls')),  # Changement de 'results' à 'results'
        path('', include('users.urls')),
    ])),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/client/', include([
        path('', include('games.urls')),
        path('', include('programmes.urls')),
        path('', include('predictions.urls')),
        path('', include('results.urls')),  # Changement de 'results' à 'results'
    ])),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]