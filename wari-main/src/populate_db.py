# populate_db.py
import os
import django
from django.utils import timezone
from datetime import datetime, timedelta

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wari.settings')
django.setup()

# Importer les modèles
from users.models import CustomUser
from games.models import Game, Country, GameType
from predictions.models import Prediction
from results.models import Result
from programmes.models import Program

def populate_database():
    """
    Script pour peupler la base de données avec des données de test.
    Crée des utilisateurs, pays, types de jeux, jeux, prédictions, résultats et programmes.
    """
    try:
        # -------------------------------------
        # Étape 1 : Nettoyage de la Base (Optionnel)
        # -------------------------------------
        print("Nettoyage des données existantes...")
        CustomUser.objects.all().delete()
        Country.objects.all().delete()
        GameType.objects.all().delete()
        Game.objects.all().delete()
        Prediction.objects.all().delete()
        Result.objects.all().delete()
        Program.objects.all().delete()
        print("Nettoyage terminé.")

        # -------------------------------------
        # Étape 2 : Création des Utilisateurs
        # -------------------------------------
        print("Création des utilisateurs...")
        # Administrateur
        admin = CustomUser.objects.create_user(
            username='admin1',
            email='admin1@example.com',
            password='password',
            role='admin',
            is_staff=True,
            is_superuser=True
        )

        # Utilisateur normal
        user1 = CustomUser.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password',
            role='user'
        )

        user2 = CustomUser.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password',
            role='user'
        )
        print(f"Utilisateurs créés : {admin.username}, {user1.username}, {user2.username}")

        # -------------------------------------
        # Étape 3 : Création des Pays
        # -------------------------------------
        print("Création des pays...")
        countries_data = [
            {"name": "France", "slug": "france"},
            {"name": "Espagne", "slug": "espagne"},
            {"name": "Italie", "slug": "italie"},
            {"name": "Allemagne", "slug": "allemagne"},
        ]

        countries = []
        for country_data in countries_data:
            country, created = Country.objects.get_or_create(
                slug=country_data["slug"],
                defaults={"name": country_data["name"]}
            )
            countries.append(country)
            print(f"Pays {'créé' if created else 'existait déjà'} : {country.name}")

        # -------------------------------------
        # Étape 4 : Création des Types de Jeux
        # -------------------------------------
        print("Création des types de jeux...")
        game_types_data = [
            {"name": "Football", "slug": "football"},
            {"name": "Basketball", "slug": "basketball"},
            {"name": "Tennis", "slug": "tennis"},
        ]

        game_types = []
        for game_type_data in game_types_data:
            game_type, created = GameType.objects.get_or_create(
                slug=game_type_data["slug"],
                defaults={"name": game_type_data["name"]}
            )
            game_types.append(game_type)
            print(f"Type de jeu {'créé' if created else 'existait déjà'} : {game_type.name}")

        # -------------------------------------
        # Étape 5 : Création des Jeux
        # -------------------------------------
        print("Création des jeux...")
        games_data = [
            {
                "name": "France vs Espagne",
                "slug": "france-vs-espagne",
                "country": countries[0],  # France
                "game_type": game_types[0],  # Football
                "is_active": True
            },
            {
                "name": "Italie vs Allemagne",
                "slug": "italie-vs-allemagne",
                "country": countries[2],  # Italie
                "game_type": game_types[0],  # Football
                "is_active": True
            },
            {
                "name": "Finale Basketball",
                "slug": "finale-basketball",
                "country": countries[1],  # Espagne
                "game_type": game_types[1],  # Basketball
                "is_active": False
            },
            {
                "name": "Tournoi de Tennis",
                "slug": "tournoi-tennis",
                "country": countries[3],  # Allemagne
                "game_type": game_types[2],  # Tennis
                "is_active": True
            },
        ]

        games = []
        for game_data in games_data:
            game, created = Game.objects.get_or_create(
                slug=game_data["slug"],
                defaults={
                    "name": game_data["name"],
                    "country": game_data["country"],
                    "game_type": game_data["game_type"],
                    "is_active": game_data["is_active"]
                }
            )
            games.append(game)
            print(f"Jeu {'créé' if created else 'existait déjà'} : {game.name}")

        # -------------------------------------
        # Étape 6 : Création des Prédictions
        # -------------------------------------
        print("Création des prédictions...")
        predictions_data = [
            {
                "game": games[0],  # France vs Espagne
                "author": user1,
                "description": "Victoire de la France 2-1",
                "is_published": True,
                "predicted_at": timezone.now() - timedelta(days=2)
            },
            {
                "game": games[0],  # France vs Espagne
                "author": user2,
                "description": "Match nul 1-1",
                "is_published": True,
                "predicted_at": timezone.now() - timedelta(days=1)
            },
            {
                "game": games[1],  # Italie vs Allemagne
                "author": user1,
                "description": "Victoire de l'Italie 3-2",
                "is_published": True,
                "predicted_at": timezone.now() - timedelta(days=3)
            },
            {
                "game": games[2],  # Finale Basketball
                "author": user2,
                "description": "Victoire de l'équipe A",
                "is_published": False,
                "predicted_at": timezone.now() - timedelta(days=4)
            },
        ]

        predictions = []
        for prediction_data in predictions_data:
            prediction = Prediction.objects.create(
                game=prediction_data["game"],
                author=prediction_data["author"],
                description=prediction_data["description"],
                is_published=prediction_data["is_published"],
                predicted_at=prediction_data["predicted_at"]
            )
            predictions.append(prediction)
            print(f"Prédiction créée pour {prediction.game.name} par {prediction.author.username}")

        # -------------------------------------
        # Étape 7 : Création des Résultats
        # -------------------------------------
        print("Création des résultats...")
        results_data = [
            {
                "game": games[0],  # France vs Espagne
                "validated_by": admin,
                "status": "official",
                "outcome": "Victoire de la France 2-1",
                "result_date": "2025-03-23"
            },
            {
                "game": games[1],  # Italie vs Allemagne
                "validated_by": admin,
                "status": "disputed",
                "outcome": "Victoire de l'Allemagne 2-1",
                "result_date": "2025-03-24"
            },
            {
                "game": games[2],  # Finale Basketball
                "validated_by": admin,
                "status": "official",
                "outcome": "Victoire de l'équipe B",
                "result_date": "2025-03-25"
            },
        ]

        results = []
        for result_data in results_data:
            result = Result.objects.create(
                game=result_data["game"],
                validated_by=result_data["validated_by"],
                status=result_data["status"],
                outcome=result_data["outcome"],
                result_date=result_data["result_date"]
            )
            results.append(result)
            print(f"Résultat créé pour {result.game.name} : {result.outcome}")

        # -------------------------------------
        # Étape 8 : Création des Programmes
        # -------------------------------------
        print("Création des programmes...")
        programs_data = [
            {
                "game": games[0],  # France vs Espagne
                "event_date": "2025-03-23T15:00:00Z",
                "details": "Match de championnat",
                "is_published": True
            },
            {
                "game": games[1],  # Italie vs Allemagne
                "event_date": "2025-03-24T18:00:00Z",
                "details": "Demi-finale",
                "is_published": True
            },
            {
                "game": games[2],  # Finale Basketball
                "event_date": "2025-03-25T20:00:00Z",
                "details": "Finale du tournoi",
                "is_published": False
            },
            {
                "game": games[3],  # Tournoi de Tennis
                "event_date": "2025-03-26T14:00:00Z",
                "details": "Quart de finale",
                "is_published": True
            },
        ]

        programs = []
        for program_data in programs_data:
            program = Program.objects.create(
                game=program_data["game"],
                event_date=program_data["event_date"],
                details=program_data["details"],
                is_published=program_data["is_published"]
            )
            programs.append(program)
            print(f"Programme créé pour {program.game.name} : {program.details}")

        # -------------------------------------
        # Étape 9 : Résumé des Données Créées
        # -------------------------------------
        print("\nRésumé des données créées :")
        print(f"- Utilisateurs : {CustomUser.objects.count()}")
        print(f"- Pays : {Country.objects.count()}")
        print(f"- Types de jeux : {GameType.objects.count()}")
        print(f"- Jeux : {Game.objects.count()}")
        print(f"- Prédictions : {Prediction.objects.count()}")
        print(f"- Résultats : {Result.objects.count()}")
        print(f"- Programmes : {Program.objects.count()}")
        print("\nBase de données peuplée avec succès !")

    except Exception as e:
        print(f"Une erreur s'est produite : {str(e)}")
        raise

if __name__ == "__main__":
    populate_database()