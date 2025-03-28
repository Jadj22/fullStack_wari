# Generated by Django 5.1.7 on 2025-03-19 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Prediction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(help_text='Détails du pronostic', verbose_name='Description')),
                ('predicted_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Date de pronostic')),
                ('is_published', models.BooleanField(db_index=True, default=False, help_text='Indique si le pronostic est visible publiquement', verbose_name='Publié')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Dernière mise à jour')),
            ],
            options={
                'verbose_name': 'Prédiction',
                'verbose_name_plural': 'Prédictions',
                'ordering': ['-predicted_at'],
            },
        ),
    ]
