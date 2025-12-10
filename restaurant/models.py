from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Categorie"
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.nom

class Plat(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField()
    prix = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    categorie = models.ForeignKey(
        Categorie, 
        on_delete=models.CASCADE,
        related_name='plats'
    )
    image = models.ImageField(
        upload_to='plats/', 
        blank=True, 
        null=True
    )
    disponible = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Plat"
        verbose_name_plural = "Plats"
        ordering = ['categorie', 'nom']
    
    def __str__(self):
        return f"{self.nom} - {self.prix} FCFA"

class Table(models.Model):
    numero = models.IntegerField(unique=True)
    capacite = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    disponible = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Table"
        verbose_name_plural = "Tables"
        ordering = ['numero']
    
    def __str__(self):
        return f"Table {self.numero} ({self.capacite} places)"

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('CONFIRMEE', 'Confirmee'),
        ('ANNULEE', 'Annulee'),
        ('TERMINEE', 'Terminee'),
    ]
    
    client_nom = models.CharField(max_length=200)
    client_telephone = models.CharField(max_length=20)
    client_email = models.EmailField(blank=True)
    table = models.ForeignKey(
        Table, 
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    nombre_personnes = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    date_reservation = models.DateTimeField()
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='EN_ATTENTE'
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"
        ordering = ['-date_reservation']
    
    def __str__(self):
        return f"{self.client_nom} - Table {self.table.numero}"

class Commande(models.Model):
    STATUS_CHOICES = [
        ('EN_COURS', 'En cours'),
        ('PRETE', 'Prete'),
        ('SERVIE', 'Servie'),
        ('PAYEE', 'Payee'),
    ]
    
    table = models.ForeignKey(
        Table, 
        on_delete=models.CASCADE,
        related_name='commandes'
    )
    serveur = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='commandes'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='EN_COURS'
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Commande #{self.id} - Table {self.table.numero}"
    
    def total(self):
        return sum(item.subtotal() for item in self.items.all())

class ItemCommande(models.Model):
    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name='items'
    )
    plat = models.ForeignKey(
        Plat,
        on_delete=models.CASCADE
    )
    quantite = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Item de commande"
        verbose_name_plural = "Items de commande"
    
    def __str__(self):
        return f"{self.quantite}x {self.plat.nom}"
    
    def subtotal(self):
        return self.quantite * self.prix_unitaire
    
    def save(self, *args, **kwargs):
        if not self.prix_unitaire:
            self.prix_unitaire = self.plat.prix
        super().save(*args, **kwargs)

class Facture(models.Model):
    METHODE_PAIEMENT_CHOICES = [
        ('ESPECE', 'Espece'),
        ('CARTE', 'Carte bancaire'),
        ('MOBILE', 'Mobile money'),
    ]
    
    commande = models.OneToOneField(
        Commande,
        on_delete=models.CASCADE,
        related_name='facture'
    )
    numero_facture = models.CharField(
        max_length=50, 
        unique=True
    )
    montant_total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    tva = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    montant_ttc = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    methode_paiement = models.CharField(
        max_length=20,
        choices=METHODE_PAIEMENT_CHOICES
    )
    date_emission = models.DateTimeField(auto_now_add=True)
    payee = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-date_emission']
    
    def __str__(self):
        return f"Facture {self.numero_facture}"
    
    def save(self, *args, **kwargs):
        if not self.numero_facture:
            from datetime import datetime
            self.numero_facture = f"FAC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if not self.montant_total:
            self.montant_total = self.commande.total()
        
        self.tva = self.montant_total * Decimal('0.18')
        self.montant_ttc = self.montant_total + self.tva
        
        super().save(*args, **kwargs)