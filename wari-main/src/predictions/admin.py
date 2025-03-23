from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Prediction

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    """Interface pour gérer les pronostics."""
    list_display = ['game', 'predicted_at', 'is_published', 'author', 'updated_at', 'short_description']
    list_filter = ['is_published', 'predicted_at', 'author', 'game__country']
    search_fields = ['game__name', 'description']
    date_hierarchy = 'predicted_at'
    list_select_related = ['game', 'author']
    list_per_page = 25
    actions = ['publish', 'unpublish']

    def short_description(self, obj):
        """Affiche un aperçu de la description (50 premiers caractères)."""
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    short_description.short_description = _('Aperçu')

    def publish(self, request, queryset):
        """Met à jour les pronostics pour les publier."""
        updated = queryset.update(is_published=True)
        self.message_user(request, f"{updated} pronostics sont maintenant publiés.")
    publish.short_description = _("Publier les pronostics")

    def unpublish(self, request, queryset):
        """Met à jour les pronostics pour les dépublier."""
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} pronostics sont maintenant dépubliés.")
    unpublish.short_description = _("Dépublier les pronostics")
