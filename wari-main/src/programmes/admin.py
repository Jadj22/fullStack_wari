from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import Program

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    """Interface pour gérer les programmes."""
    list_display = ['game', 'event_date', 'is_published', 'created_at', 'days_until_event']
    list_filter = ['is_published', 'event_date', 'game__country']
    search_fields = ['game__name', 'details']
    date_hierarchy = 'event_date'
    list_select_related = ['game', 'game__country']
    list_per_page = 25
    actions = ['publish', 'unpublish']

    def days_until_event(self, obj):
        """Calcule le nombre de jours avant l'événement."""
        delta = obj.event_date - timezone.now()
        return delta.days if delta.days > 0 else "Passé"
    days_until_event.short_description = _('Jours restants')

    def publish(self, request, queryset):
        """Met à jour les programmes pour les publier."""
        updated = queryset.update(is_published=True)
        self.message_user(request, f"{updated} programmes sont maintenant publiés.")
    publish.short_description = _("Publier les programmes")

    def unpublish(self, request, queryset):
        """Met à jour les programmes pour les dépublier."""
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} programmes sont maintenant dépubliés.")
    unpublish.short_description = _("Dépublier les programmes")
