from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import CustomUser
from games.models import Game


class Prediction(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='predictions',
        verbose_name='Jeu',
        help_text='Le jeu auquel ce pronostic est associé'
    )
    description = models.TextField(
        verbose_name='Description',
        help_text='Détails du pronostic'
    )
    predicted_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Date de pronostic',
        editable=False
    )
    is_published = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='Publié',
        help_text='Indique si le pronostic est visible publiquement'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='predictions',
        verbose_name='Auteur',
        help_text='Utilisateur ayant créé le pronostic'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Dernière mise à jour',
        editable=False
    )

    class Meta:
        indexes = [
            models.Index(fields=['is_published', 'predicted_at']),
            models.Index(fields=['game', 'is_published']),
        ]
        verbose_name = 'Prédiction'
        verbose_name_plural = 'Prédictions'
        ordering = ['-predicted_at']

    def __str__(self):
        date_str = self.predicted_at.strftime('%d/%m/%Y %H:%M')
        return f"Prédiction pour {self.game} le {date_str} - Publiée : {self.is_published}"

    def clean(self):
        if not self.description.strip():
            raise ValidationError("La description ne peut pas être vide.")
        if self.is_published and not self.author:
            raise ValidationError("Un pronostic publié doit avoir un auteur.")

    def save(self, *args, **kwargs):
        self.description = self.description.strip()
        self.full_clean()
        super().save(*args, **kwargs)
