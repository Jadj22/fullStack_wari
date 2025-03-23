from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import CustomUser
from games.models import Game

class Result(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('official', 'Officiel'),
        ('disputed', 'Contesté'),
    )

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='Jeu',
        help_text='Le jeu auquel ce résultat est associé'
    )
    result_date = models.DateTimeField(
        db_index=True,
        verbose_name='Date du résultat',
        help_text='Date et heure auxquelles le résultat a été enregistré'
    )
    outcome = models.TextField(
        verbose_name='Résultat (texte libre)',
        help_text='Description détaillée du résultat en texte brut',
        blank=True
    )
    outcome_details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Détails structurés',
        help_text='Résultat au format JSON (ex. : {"score": "2-1", "winner": "Équipe A"})'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        verbose_name='Statut',
        help_text='Statut actuel du résultat'
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
    validated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_results',
        verbose_name='Validé par',
        help_text='Administrateur ayant officialisé le résultat'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['game', 'result_date'],
                name='unique_result_per_game_date'
            )
        ]
        indexes = [
            models.Index(fields=['result_date', 'status']),
            models.Index(fields=['game', 'result_date']),
            models.Index(fields=['status', 'validated_by']),
        ]
        verbose_name = 'Résultat'
        verbose_name_plural = 'Résultats'
        ordering = ['-result_date']

    def __str__(self):
        date_str = self.result_date.strftime('%d/%m/%Y %H:%M')
        return f"Résultat pour {self.game} le {date_str} - {self.get_status_display()}"

    def clean(self):
        if not self.outcome.strip() and not self.outcome_details:
            raise ValidationError("Au moins un des champs 'Résultat' ou 'Détails structurés' doit être rempli.")
        if self.result_date > timezone.now():
            raise ValidationError("La date du résultat ne peut pas être dans le futur.")
        if self.status == 'official' and not self.validated_by:
            raise ValidationError("Un résultat officiel doit avoir un validateur.")

    def save(self, *args, **kwargs):
        if self.outcome:
            self.outcome = self.outcome.strip()
        if not self.outcome_details:
            self.outcome_details = {}
        self.full_clean()
        super().save(*args, **kwargs)