from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Interface d'administration pour gérer les utilisateurs."""
    # Colonnes affichées dans la liste
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active', 'date_joined']
    # Filtres disponibles dans la barre latérale
    list_filter = ['role', 'is_staff', 'is_active', 'date_joined']
    # Recherche par champs texte
    search_fields = ['username', 'email']
    # Optimisation des requêtes pour éviter les N+1
    list_select_related = ['groups']
    # Limite d'éléments par page pour la performance
    list_per_page = 25
    # Ajout du champ personnalisé 'role' au formulaire
    fieldsets = UserAdmin.fieldsets + (
        (_('Rôle personnalisé'), {'fields': ('role',)}),
    )
    # Actions personnalisées pour modifier les utilisateurs en masse
    actions = ['make_admin', 'make_viewer', 'toggle_active']

    def make_admin(self, request, queryset):
        """Met à jour le rôle en 'admin' et active les privilèges staff."""
        updated = queryset.update(role='admin', is_staff=True, is_superuser=False)
        self.message_user(request, f"{updated} utilisateurs sont maintenant administrateurs.")
    make_admin.short_description = _("Promouvoir en administrateur")

    def make_viewer(self, request, queryset):
        """Met à jour le rôle en 'viewer' et supprime les privilèges."""
        updated = queryset.update(role='viewer', is_staff=False, is_superuser=False)
        self.message_user(request, f"{updated} utilisateurs sont maintenant spectateurs.")
    make_viewer.short_description = _("Rétrograder en spectateur")

    def toggle_active(self, request, queryset):
        """Active ou désactive les utilisateurs sélectionnés."""
        for user in queryset:
            user.is_active = not user.is_active
            user.save()
        self.message_user(request, "L'état actif des utilisateurs sélectionnés a été modifié.")
    toggle_active.short_description = _("Basculer l'état actif")

