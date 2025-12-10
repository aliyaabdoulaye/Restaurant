from django.contrib import admin
from .models import *

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'description']
    search_fields = ['nom']

@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    list_display = [
        'nom', 
        'categorie', 
        'prix', 
        'disponible'
    ]
    list_filter = ['categorie', 'disponible']
    search_fields = ['nom', 'description']
    list_editable = ['disponible']

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['numero', 'capacite', 'disponible']
    list_filter = ['disponible']
    list_editable = ['disponible']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = [
        'client_nom',
        'table',
        'date_reservation',
        'nombre_personnes',
        'statut'
    ]
    list_filter = ['statut', 'date_reservation']
    search_fields = [
        'client_nom', 
        'client_telephone', 
        'client_email'
    ]

class ItemCommandeInline(admin.TabularInline):
    model = ItemCommande
    extra = 1

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'table', 
        'serveur', 
        'statut', 
        'date_creation'
    ]
    list_filter = ['statut', 'date_creation']
    inlines = [ItemCommandeInline]

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = [
        'numero_facture',
        'commande',
        'montant_ttc',
        'methode_paiement',
        'payee',
        'date_emission'
    ]
    list_filter = ['payee', 'methode_paiement', 'date_emission']
    search_fields = ['numero_facture']