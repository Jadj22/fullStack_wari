from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from games.models import Game

class Program(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='programs',
        verbose_name='Jeu',
        help_text='Le jeu auquel ce programme est associé'
    )
    event_date = models.DateTimeField(
        db_index=True,
        verbose_name='Date de l’événement',
        help_text='Date et heure de l’événement'
    )
    details = models.TextField(
        blank=True,
        verbose_name='Détails',
        help_text='Description ou informations supplémentaires'
    )
    is_published = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='Publié',
        help_text='Indique si le programme est visible publiquement'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création',
        editable=False
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Dernière mise à jour',
        editable=False
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['game', 'event_date'],
                name='unique_program_per_game_date'
            )
        ]
        indexes = [
            models.Index(fields=['event_date', 'is_published']),
            models.Index(fields=['game', 'event_date']),
        ]
        verbose_name = 'Programme'
        verbose_name_plural = 'Programmes'
        ordering = ['event_date']

    def __str__(self):
        date_str = self.event_date.strftime('%d/%m/%Y %H:%M')
        return f"Programme pour {self.game} le {date_str}"

    def clean(self):
        if self.event_date < timezone.now() and self.is_published:
            raise ValidationError("Un programme passé ne peut pas être publié.")

    def save(self, *args, **kwargs):
        if self.details:
            self.details = self.details.strip()
        self.full_clean()
        super().save(*args, **kwargs)