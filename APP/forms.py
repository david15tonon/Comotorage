from django import forms
from .models import Profile, OffreCovoiturage
from django.contrib.auth.models import User

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'bio', 'phone', 'avatar',
            'depart_location', 'heure_depart', 'heure_arrivee',
            'is_driver', 'marque_vehicule', 'modele_vehicule', 'places_disponibles'
        ]

class OffreCovoiturageForm(forms.ModelForm):
    class Meta:
        model = OffreCovoiturage
        fields = ['point_depart', 'point_arrivee', 'heure_depart', 'places_disponibles', 'prix', 'description']
        widgets = {
            'heure_depart': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'placeholder': "Ajoutez des détails sur votre trajet..."}),
            'point_depart': forms.TextInput(attrs={'placeholder': "Ex: Calavi, Tankpè"}),
            'point_arrivee': forms.TextInput(attrs={'placeholder': "Ex: IFRI, UAC"}),
        }

from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'bio', 'phone', 'avatar',
            'depart_location', 'heure_depart', 'heure_arrivee',
            'latitude', 'longitude', 'is_driver',
            'marque_vehicule', 'modele_vehicule', 'places_disponibles'
        ]
        widgets = {
            'heure_depart': forms.TimeInput(attrs={'type': 'time'}),
            'heure_arrivee': forms.TimeInput(attrs={'type': 'time'}),
        }
