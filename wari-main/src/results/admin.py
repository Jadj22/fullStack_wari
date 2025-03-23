from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Result

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    """Interface pour gérer les résultats."""
    list_display = ['game', 'result_date', 'status', 'validated_by', 'created_at', 'short_outcome']
    list_filter = ['status', 'result_date', 'validated_by', 'game__country']
    search_fields = ['game__name', 'outcome']
    date_hierarchy = 'result_date'
    list_select_related = ['game', 'validated_by']
    list_per_page = 25
    actions = ['mark_official', 'mark_pending']

    def short_outcome(self, obj):
        """Affiche un aperçu du résultat (50 premiers caractères)."""
        return obj.outcome[:50] + '...' if len(obj.outcome) > 50 else obj.outcome
    short_outcome.short_description = _('Résultat court')

    def mark_official(self, request, queryset):
        """Met à jour les résultats comme officiels avec l'utilisateur actuel."""
        user = request.user if request.user.is_authenticated else None
        updated = queryset.update(status='official', validated_by=user)
        self.message_user(request, f"{updated} résultats sont maintenant officiels.")
    mark_official.short_description = _("Marquer comme officiel")

    def mark_pending(self, request, queryset):
        """Met à jour les résultats comme en attente et supprime le validateur."""
        updated = queryset.update(status='pending', validated_by=None)
        self.message_user(request, f"{updated} résultats sont maintenant en attente.")
    mark_pending.short_description = _("Marquer comme en attente")
