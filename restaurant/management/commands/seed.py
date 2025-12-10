from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from restaurant.models import Categorie, Plat, Table, Commande, ItemCommande
from decimal import Decimal


class Command(BaseCommand):
    help = "Insère les données de base pour le test"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING(" Insertion des données..."))

        # --- UTILISATEUR / SERVEUR ---
        serveur, created = User.objects.get_or_create(
            username="serveur1",
            defaults={
                "first_name": "Ali",
                "last_name": "Serveur",
                "email": "serveur@example.com"
            }
        )
        if created:
            serveur.set_password("password123")
            serveur.save()

        # --- CATEGORIES ---
        categories = {
            "Entrées": "Petites entrées pour commencer",
            "Plats principaux": "Plats chauds et consistants",
            "Desserts": "Douceurs sucrées",
            "Boissons": "Boissons fraîches et chaudes"
        }

        cat_objs = {}
        for nom, desc in categories.items():
            cat, _ = Categorie.objects.get_or_create(nom=nom, defaults={"description": desc})
            cat_objs[nom] = cat

        # --- PLATS ---
        plats = [
            ("Salade César", "Salade croquante avec poulet grillé", 2500, "Entrées"),
            ("Soupe du jour", "Préparée quotidiennement", 1800, "Entrées"),

            ("Poulet braisé", "Poulet assaisonné et grillé", 5000, "Plats principaux"),
            ("Steak frites", "Steak tendre + Frites maison", 6500, "Plats principaux"),
            ("Riz au poisson", "Spécialité locale", 4000, "Plats principaux"),

            ("Tarte aux pommes", "Tarte faite maison", 2000, "Desserts"),
            ("Crème glacée", "3 boules au choix", 1500, "Desserts"),

            ("Coca-Cola", "Bouteille 33cl", 700, "Boissons"),
            ("Jus naturel", "Fait maison", 1200, "Boissons"),
        ]

        for nom, desc, prix, cat_nom in plats:
            Plat.objects.get_or_create(
                nom=nom,
                defaults={
                    "description": desc,
                    "prix": Decimal(prix),
                    "categorie": cat_objs[cat_nom],
                }
            )

        # --- TABLES ---
        for i in range(1, 11):  # 10 tables
            Table.objects.get_or_create(
                numero=i,
                defaults={
                    "capacite": 4 if i <= 5 else 6,
                    "disponible": True
                }
            )

        # --- COMMANDE D'EXEMPLE ---
        table1 = Table.objects.get(numero=1)

        commande = Commande.objects.create(
            table=table1,
            serveur=serveur,
            statut="EN_COURS"
        )

        # On prend quelques plats existants
        plats = Plat.objects.all()[:3]

        for plat in plats:
            ItemCommande.objects.create(
                commande=commande,
                plat=plat,
                quantite=1,
                prix_unitaire=plat.prix
            )

        self.stdout.write(self.style.SUCCESS("Données insérées avec succès !"))
