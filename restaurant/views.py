from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import HttpResponse
from .models import *
from .forms import *
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('/')

def index(request):
    """Page d'accueil"""
    categories = Categorie.objects.all()
    plats_populaires = Plat.objects.filter(
        disponible=True
    )[:6]
    
    context = {
        'categories': categories,
        'plats_populaires': plats_populaires,
    }
    return render(request, 'restaurant/index.html', context)

def menu(request):
    """Affichage du menu complet"""
    categories = Categorie.objects.prefetch_related('plats').all()
    
    # Filtrage par categorie
    categorie_id = request.GET.get('categorie')
    if categorie_id:
        plats = Plat.objects.filter(
            categorie_id=categorie_id,
            disponible=True
        )
    else:
        plats = Plat.objects.filter(disponible=True)
    
    # Recherche
    search = request.GET.get('search')
    if search:
        plats = plats.filter(
            Q(nom__icontains=search) | 
            Q(description__icontains=search)
        )
    
    context = {
        'categories': categories,
        'plats': plats,
        'selected_categorie': categorie_id,
    }
    return render(request, 'restaurant/menu.html', context)

@login_required
def gestion_tables(request):
    """Gestion des tables"""
    tables = Table.objects.all()
    
    # Tables disponibles
    tables_disponibles = tables.filter(disponible=True)
    tables_occupees = tables.filter(disponible=False)
    
    context = {
        'tables': tables,
        'tables_disponibles': tables_disponibles,
        'tables_occupees': tables_occupees,
    }
    return render(request, 'restaurant/tables.html', context)

@login_required
def toggle_table(request, table_id):
    """Changer la disponibilite d'une table"""
    table = get_object_or_404(Table, id=table_id)
    table.disponible = not table.disponible
    table.save()
    
    status = "disponible" if table.disponible else "occupee"
    messages.success(
        request, 
        f"Table {table.numero} est maintenant {status}"
    )
    return redirect('gestion_tables')

def reservation(request):
    """Systeme de reservation"""
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save()
            messages.success(
                request,
                'Votre reservation a ete enregistree avec succes!'
            )
            return redirect('confirmation_reservation', pk=reservation.id)
    else:
        form = ReservationForm()
    
    tables_disponibles = Table.objects.filter(disponible=True)
    
    context = {
        'form': form,
        'tables_disponibles': tables_disponibles,
    }
    return render(request, 'restaurant/reservation.html', context)

def confirmation_reservation(request, pk):
    """Confirmation de reservation"""
    reservation = get_object_or_404(Reservation, pk=pk)
    return render(
        request, 
        'restaurant/confirmation_reservation.html',
        {'reservation': reservation}
    )

@login_required
def liste_reservations(request):
    """Liste des reservations"""
    date_filter = request.GET.get('date')
    statut_filter = request.GET.get('statut')
    
    reservations = Reservation.objects.all()
    
    if date_filter:
        reservations = reservations.filter(
            date_reservation__date=date_filter
        )
    
    if statut_filter:
        reservations = reservations.filter(statut=statut_filter)
    
    context = {
        'reservations': reservations,
    }
    return render(
        request, 
        'restaurant/liste_reservations.html', 
        context
    )

@login_required
def creer_commande(request, table_id):
    """Creer une nouvelle commande"""
    table = get_object_or_404(Table, id=table_id)
    
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            commande = form.save(commit=False)
            commande.table = table
            commande.serveur = request.user
            commande.save()
            
            table.disponible = False
            table.save()
            
            messages.success(
                request,
                f'Commande creee pour la table {table.numero}'
            )
            return redirect('ajouter_items', commande_id=commande.id)
    else:
        form = CommandeForm()
    
    context = {
        'form': form,
        'table': table,
    }
    return render(request, 'restaurant/creer_commande.html', context)

@login_required
def ajouter_items(request, commande_id):
    """Ajouter des items a une commande"""
    commande = get_object_or_404(Commande, id=commande_id)
    
    if request.method == 'POST':
        form = ItemCommandeForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.commande = commande
            item.save()
            
            messages.success(
                request,
                f'{item.quantite}x {item.plat.nom} ajoute'
            )
            return redirect('ajouter_items', commande_id=commande.id)
    else:
        form = ItemCommandeForm()
    
    items = commande.items.all()
    total = commande.total()
    
    context = {
        'form': form,
        'commande': commande,
        'items': items,
        'total': total,
    }
    return render(request, 'restaurant/ajouter_items.html', context)

@login_required
def liste_commandes(request):
    """Liste des commandes"""
    statut_filter = request.GET.get('statut')
    
    commandes = Commande.objects.select_related(
        'table', 'serveur'
    ).prefetch_related('items__plat')
    
    if statut_filter:
        commandes = commandes.filter(statut=statut_filter)
    
    context = {
        'commandes': commandes,
    }
    return render(request, 'restaurant/liste_commandes.html', context)

@login_required
def detail_commande(request, commande_id):
    """Detail d'une commande"""
    commande = get_object_or_404(
        Commande.objects.prefetch_related('items__plat'),
        id=commande_id
    )
    
    context = {
        'commande': commande,
        'total': commande.total(),
    }
    return render(request, 'restaurant/detail_commande.html', context)


@login_required
def generer_facture(request, commande_id):
    """Generer une facture"""
    commande = get_object_or_404(Commande, id=commande_id)
    
    total = commande.total()                     # total est déjà un Decimal
    tva_rate = Decimal("0.18")                  # taux de TVA en Decimal
    
    tva = total * tva_rate                       # OK
    ttc = total + tva                            # OK
    
    if request.method == 'POST':
        methode_paiement = request.POST.get('methode_paiement')
        
        facture = Facture.objects.create(
            commande=commande,
            methode_paiement=methode_paiement
        )
        
        commande.statut = 'PAYEE'
        commande.save()
        
        commande.table.disponible = True
        commande.table.save()
        
        messages.success(
            request,
            f'Facture {facture.numero_facture} generee'
        )
        return redirect('detail_facture', facture_id=facture.id)
    
    context = {
        'commande': commande,
        'total': total,
        'tva': tva,
        'ttc': ttc,
    }
    return render(request, 'restaurant/generer_facture.html', context)



@login_required
def detail_facture(request, facture_id):
    """Detail d'une facture"""
    facture = get_object_or_404(
        Facture.objects.select_related('commande__table'),
        id=facture_id
    )
    
    context = {
        'facture': facture,
    }
    return render(request, 'restaurant/detail_facture.html', context)

@login_required
def liste_factures(request):
    """Liste des factures"""
    factures = Facture.objects.select_related(
        'commande__table'
    ).order_by('-date_emission')
    
    # Statistiques
    total_factures = factures.aggregate(
        Sum('montant_ttc')
    )['montant_ttc__sum'] or 0
    
    context = {
        'factures': factures,
        'total_factures': total_factures,
    }
    return render(request, 'restaurant/liste_factures.html', context)

@login_required
def dashboard(request):
    """Tableau de bord"""
    today = datetime.now().date()
    
    # Statistiques du jour
    commandes_jour = Commande.objects.filter(
        date_creation__date=today
    )
    
    reservations_jour = Reservation.objects.filter(
        date_reservation__date=today
    )
    
    factures_jour = Facture.objects.filter(
        date_emission__date=today
    )
    
    chiffre_affaires_jour = factures_jour.aggregate(
        Sum('montant_ttc')
    )['montant_ttc__sum'] or 0
    
    tables_occupees = Table.objects.filter(
        disponible=False
    ).count()
    
    context = {
        'commandes_jour': commandes_jour.count(),
        'reservations_jour': reservations_jour.count(),
        'chiffre_affaires_jour': chiffre_affaires_jour,
        'tables_occupees': tables_occupees,
        'commandes_recentes': commandes_jour[:5],
        'reservations_recentes': reservations_jour[:5],
    }
    return render(request, 'restaurant/dashboard.html', context)