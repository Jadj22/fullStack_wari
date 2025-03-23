from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nom')
    code = models.CharField(max_length=3, unique=True, verbose_name='Code ISO')
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Pays'
        verbose_name_plural = 'Pays'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.name = self.name.strip().title()
        super().save(*args, **kwargs)

class GameType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Nom du type')
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Type de jeu'
        verbose_name_plural = 'Types de jeux'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.name = self.name.strip().title()
        super().save(*args, **kwargs)

class Game(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Nom')
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    game_type = models.ForeignKey(GameType, on_delete=models.PROTECT, related_name='games')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='games')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True, verbose_name='Description')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'country'], name='unique_game_per_country')
        ]
        indexes = [
            models.Index(fields=['game_type', 'country']),
            models.Index(fields=['name', 'game_type']),
        ]
        ordering = ['-created_at']
        verbose_name = 'Jeu'
        verbose_name_plural = 'Jeux'

    def __str__(self):
        # Protection contre game_type=None dans l'affichage
        game_type_name = self.game_type.name if self.game_type else 'Type non défini'
        country_name = self.country.name if self.country else 'Sans Pays'
        return f"{self.name} ({game_type_name} - {country_name})"

    def clean(self):
        if not self.name.strip():
            raise ValidationError("Le nom du jeu ne peut pas être vide.")
        if len(self.name) < 3:
            raise ValidationError("Le nom du jeu doit comporter au moins 3 caractères.")
        if self.country is None:
            raise ValidationError("Le pays est obligatoire.")
        if self.game_type is None:
            raise ValidationError("Le type de jeu est obligatoire.")

    def save(self, *args, **kwargs):
        self.name = self.name.strip().title()
        if not self.slug:
            country_code = self.country.code.lower() if self.country else "unknown"
            self.slug = slugify(f"{self.name}-{country_code}")
        self.full_clean()
        super().save(*args, **kwargs)