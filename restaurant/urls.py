from django.urls import path
from . import views

urlpatterns = [
    # Pages publiques
    path('', views.index, name='index'),
    path('menu/', views.menu, name='menu'),
    path('reservation/', views.reservation, name='reservation'),
    path('reservation/<int:pk>/confirmation/', 
         views.confirmation_reservation, 
         name='confirmation_reservation'),
    
    # Gestion (authentification requise)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),

    
    # Tables
    path('tables/', views.gestion_tables, name='gestion_tables'),
    path('tables/<int:table_id>/toggle/', 
         views.toggle_table, 
         name='toggle_table'),
    
    # Reservations
    path('reservations/', 
         views.liste_reservations, 
         name='liste_reservations'),
    
    # Commandes
    path('commandes/', views.liste_commandes, name='liste_commandes'),
    path('commandes/<int:commande_id>/', 
         views.detail_commande, 
         name='detail_commande'),
    path('tables/<int:table_id>/commande/', 
         views.creer_commande, 
         name='creer_commande'),
    path('commandes/<int:commande_id>/items/', 
         views.ajouter_items, 
         name='ajouter_items'),
    
    # Factures
    path('factures/', views.liste_factures, name='liste_factures'),
    path('factures/<int:facture_id>/', 
         views.detail_facture, 
         name='detail_facture'),
    path('commandes/<int:commande_id>/facturer/', 
         views.generer_facture, 
         name='generer_facture'),
]