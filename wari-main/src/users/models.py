from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLES = (
        ('admin', 'Administrateur'),
        ('editor', 'Éditeur'),
        ('viewer', 'Spectateur'),
    )
    role = models.CharField(
        max_length=10,
        choices=ROLES,
        default='admin',
        verbose_name='Rôle',
        help_text='Rôle de l’utilisateur dans le système'
    )

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return self.username
# Create your models here.
