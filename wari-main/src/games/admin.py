from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from .models import Country, GameType, Game

class GameInline(admin.TabularInline):
    """Permet d'éditer les jeux directement dans l'interface d'un pays."""
    model = Game
    extra = 0  # Pas de lignes vides par défaut lors de l'ajout
    fields = ['name', 'game_type', 'is_active']
    show_change_link = True  # Lien vers le détail du jeu

    def get_queryset(self, request):
        # Optimisation : Précharger game_type pour éviter les requêtes N+1
        return super().get_queryset(request).select_related('game_type')

    def has_add_permission(self, request, obj=None):
        # Désactiver l'ajout de jeux lors de la création d'un pays
        return False if obj is None else True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Préremplir le champ country avec le pays en cours d'édition
        if db_field.name == 'country' and hasattr(request, 'resolver_match'):
            kwargs['initial'] = request.resolver_match.kwargs.get('object_id')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """Interface pour gérer les pays."""
    list_display = ['name', 'code', 'slug', 'game_count', 'created_at']
    search_fields = ['name', 'code']
    list_filter = ['created_at']
    inlines = [GameInline]
    list_per_page = 25
    readonly_fields = ['slug', 'created_at']
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'slug')
        }),
        (_('Détails'), {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        # Optimisation : Ajouter une annotation pour game_count
        return super().get_queryset(request).annotate(game_count=Count('games'))

    def game_count(self, obj):
        """Calcule le nombre de jeux associés au pays."""
        return obj.game_count
    game_count.short_description = _('Jeux')

@admin.register(GameType)
class GameTypeAdmin(admin.ModelAdmin):
    """Interface pour gérer les types de jeux."""
    list_display = ['name', 'slug', 'game_count', 'created_at', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at', 'updated_at']
    list_per_page = 25
    readonly_fields = ['slug', 'created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        (_('Détails'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        # Optimisation : Ajouter une annotation pour game_count
        return super().get_queryset(request).annotate(game_count=Count('games'))

    def game_count(self, obj):
        """Calcule le nombre de jeux liés au type de jeu."""
        return obj.game_count
    game_count.short_description = _('Nombre de jeux')

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """Interface pour gérer les jeux."""
    list_display = ['name', 'game_type', 'country', 'is_active', 'created_at', 'updated_at']
    list_filter = ['game_type', 'country', 'is_active', 'created_at', 'updated_at']
    search_fields = ['name', 'slug']
    list_select_related = ['game_type', 'country']
    list_per_page = 25
    readonly_fields = ['slug', 'created_at', 'updated_at']
    actions = ['activate', 'deactivate']
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'game_type', 'country', 'is_active')
        }),
        (_('Détails'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def activate(self, request, queryset):
        """Met à jour les jeux pour les rendre actifs."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} jeux sont maintenant actifs.")
    activate.short_description = _("Activer les jeux")

    def deactivate(self, request, queryset):
        """Met à jour les jeux pour les désactiver."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} jeux sont maintenant désactivés.")
    deactivate.short_description = _("Désactiver les jeux")