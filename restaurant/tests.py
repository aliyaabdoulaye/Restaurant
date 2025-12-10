from django.test import TestCase, Client
from django.contrib.auth.models import User
from decimal import Decimal
from .models import *

class ModelTests(TestCase):
    def setUp(self):
        self.categorie = Categorie.objects.create(
            nom="Entrées",
            description="Entrées diverses"
        )
        
        self.plat = Plat.objects.create(
            nom="Salade César",
            description="Salade fraîche",
            prix=Decimal('5000.00'),
            categorie=self.categorie,
            disponible=True
        )
        
        self.table = Table.objects.create(
            numero=1,
            capacite=4,
            disponible=True
        )
        
        self.user = User.objects.create_user(
            username='serveur1',
            password='password123'
        )
    
    def test_plat_creation(self):
        """Test création d'un plat"""
        self.assertEqual(self.plat.nom, "Salade César")
        self.assertEqual(self.plat.prix, Decimal('5000.00'))
        self.assertTrue(self.plat.disponible)
    
    def test_table_disponibilite(self):
        """Test disponibilité table"""
        self.assertTrue(self.table.disponible)
        self.table.disponible = False
        self.table.save()
        self.assertFalse(self.table.disponible)
    
    def test_commande_creation(self):
        """Test création commande"""
        commande = Commande.objects.create(
            table=self.table,
            serveur=self.user,
            statut='EN_COURS'
        )
        self.assertEqual(commande.statut, 'EN_COURS')
        self.assertEqual(commande.table, self.table)
    
    def test_item_commande_subtotal(self):
        """Test calcul sous-total item"""
        commande = Commande.objects.create(
            table=self.table,
            serveur=self.user
        )
        
        item = ItemCommande.objects.create(
            commande=commande,
            plat=self.plat,
            quantite=2,
            prix_unitaire=self.plat.prix
        )
        
        expected = Decimal('10000.00')
        self.assertEqual(item.subtotal(), expected)
    
    def test_facture_generation(self):
        """Test génération facture"""
        commande = Commande.objects.create(
            table=self.table,
            serveur=self.user
        )
        
        ItemCommande.objects.create(
            commande=commande,
            plat=self.plat,
            quantite=2,
            prix_unitaire=self.plat.prix
        )
        
        facture = Facture.objects.create(
            commande=commande,
            methode_paiement='ESPECE'
        )
        
        self.assertIsNotNone(facture.numero_facture)
        self.assertEqual(facture.montant_total, Decimal('10000.00'))


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='admin',
            password='admin123'
        )
        
        categorie = Categorie.objects.create(nom="Test")
        self.plat = Plat.objects.create(
            nom="Plat Test",
            description="Description",
            prix=Decimal('5000.00'),
            categorie=categorie
        )
    
    def test_index_view(self):
        """Test page d'accueil"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Restaurant Pro')
    
    def test_menu_view(self):
        """Test page menu"""
        response = self.client.get('/menu/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Plat Test')
    
    def test_dashboard_requires_login(self):
        """Test authentification dashboard"""
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirect
        
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)