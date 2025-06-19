from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

#Inscription de l'utilisateur:

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Obligatoire. Exemple: email@domaine.com')
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
# Profile utilisateurs
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    depart_location = models.CharField(max_length=255, blank=True)  # Adresse
    heure_depart = models.TimeField(blank=True, null=True)
    heure_arrivee = models.TimeField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    #Informations concernant la voiture
    is_driver = models.BooleanField(default=False)  # pour filtrer
    marque_vehicule = models.CharField(max_length=100, blank=True)
    modele_vehicule = models.CharField(max_length=100, blank=True)
    places_disponibles = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.user.email}"



class OffreCovoiturage(models.Model):
    conducteur = models.ForeignKey(User, on_delete=models.CASCADE)
    point_depart = models.CharField(max_length=255)
    point_arrivee = models.CharField(max_length=255)
    heure_depart = models.DateTimeField()
    places_disponibles = models.PositiveIntegerField()
    prix = models.DecimalField(max_digits=8, decimal_places=2, default=0)  # <-- Ajoute ce champ
    description = models.TextField(blank=True, null=True)  # <-- Ajoute ce champ

    def __str__(self):
        return f"{self.conducteur.username} - {self.point_depart} vers {self.point_arrivee}"

class DemandeCovoiturage(models.Model):
    passager = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='demandes')
    point_depart = models.CharField(max_length=255)
    point_arrivee = models.CharField(max_length=255)
    heure_souhaitee = models.DateTimeField()
    date_publication = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Demande de {self.passager.user.get_full_name()} - {self.point_depart} à {self.point_arrivee}"


class Matching(models.Model):
    offre = models.ForeignKey(OffreCovoiturage, on_delete=models.CASCADE)
    demande = models.ForeignKey(DemandeCovoiturage, on_delete=models.CASCADE)
    score_compatibilite = models.FloatField(default=0.0)
    date_matching = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Match entre {self.offre.conducteur.user.get_full_name()} et {self.demande.passager.user.get_full_name()}"


class Message(models.Model):
    expediteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_envoyes')
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_recus')
    texte = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    def __str__(self):
        return f"Message de {self.expediteur.get_full_name()} à {self.destinataire.get_full_name()}"


class Conversation(models.Model):
    participants = models.ManyToManyField(User)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation entre {', '.join([user.get_full_name() for user in self.participants.all()])}"
