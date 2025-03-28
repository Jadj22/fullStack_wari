# Generated by Django 5.1.7 on 2025-03-19 12:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Nom du pays (ex. : France)', max_length=100, unique=True, verbose_name='Nom')),
                ('code', models.CharField(help_text='Code ISO 3166-1 alpha-3 (ex. : FRA)', max_length=3, unique=True, verbose_name='Code ISO')),
                ('slug', models.SlugField(blank=True, help_text='Utilisé pour les URL (généré automatiquement)', max_length=100, unique=True, verbose_name='Slug')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
            ],
            options={
                'verbose_name': 'Pays',
                'verbose_name_plural': 'Pays',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='GameType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Nom unique pour ce type de jeu (ex. : Sportif, Hippique)', max_length=50, unique=True, verbose_name='Nom du type')),
                ('slug', models.SlugField(blank=True, help_text='Utilisé pour les URL (généré automatiquement)', unique=True, verbose_name='Slug')),
                ('description', models.TextField(blank=True, help_text='Description optionnelle du type de jeu', verbose_name='Description')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Dernière mise à jour')),
            ],
            options={
                'verbose_name': 'Type de jeu',
                'verbose_name_plural': 'Types de jeux',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Nom du jeu (ex. : Tour de France)', max_length=100, verbose_name='Nom')),
                ('slug', models.SlugField(blank=True, help_text='Utilisé pour les URL (généré automatiquement)', max_length=100, unique=True, verbose_name='Slug')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Dernière mise à jour')),
                ('is_active', models.BooleanField(default=True, help_text='Indique si le jeu est actuellement disponible', verbose_name='Actif')),
                ('country', models.ForeignKey(help_text='Pays où le jeu est organisé', on_delete=django.db.models.deletion.CASCADE, related_name='games', to='games.country', verbose_name='Pays')),
                ('game_type', models.ForeignKey(help_text='Catégorie du jeu', on_delete=django.db.models.deletion.PROTECT, related_name='games', to='games.gametype', verbose_name='Type de jeu')),
            ],
            options={
                'verbose_name': 'Jeu',
                'verbose_name_plural': 'Jeux',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['game_type', 'country'], name='games_game_game_ty_0cdeea_idx'), models.Index(fields=['name', 'game_type'], name='games_game_name_a0b2bf_idx')],
                'constraints': [models.UniqueConstraint(fields=('name', 'country'), name='unique_game_per_country')],
            },
        ),
    ]
