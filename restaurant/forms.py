from django import forms
from .models import *

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'client_nom',
            'client_telephone',
            'client_email',
            'table',
            'nombre_personnes',
            'date_reservation',
            'notes'
        ]
        widgets = {
            'date_reservation': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class ItemCommandeForm(forms.ModelForm):
    class Meta:
        model = ItemCommande
        fields = ['plat', 'quantite', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

class PlatForm(forms.ModelForm):
    class Meta:
        model = Plat
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }