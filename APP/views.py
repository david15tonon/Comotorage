from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserRegisterForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import OffreCovoiturage,DemandeCovoiturage
from .models import Profile
from .forms import ProfileForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse, NoReverseMatch
from django.contrib.auth import logout
from decimal import Decimal
from datetime import datetime
from django.utils.dateparse import parse_datetime

# Create your views here.

def connexion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')  # redirige vers la page d'accueil
        else:
            erreur = "Nom d'utilisateur ou mot de passe incorrect"
            return render(request, 'APP/connexion.html', {'erreur': erreur})

    # Sinon afficher le formulaire
    return render(request, 'APP/connexion.html')

def deconnexion(request):
    logout(request)
    return redirect('connexion')

def index(request):
    return render(request, 'APP/index.html', {'information': ""})

def accueil(request):
    return render(request, 'APP/accueil.html', {'information': ""})



@login_required
def rechercher(request):
    offres = OffreCovoiturage.objects.all()

    # Récupération des filtres dans GET (recherche)
    point_depart = request.GET.get('departure', '').strip()
    point_arrivee = request.GET.get('destination', '').strip()
    date_str = request.GET.get('date', '').strip()

    if point_depart:
        offres = offres.filter(point_depart__icontains=point_depart)
    if point_arrivee:
        offres = offres.filter(point_arrivee__icontains=point_arrivee)
    if date_str:
        # on filtre par date (date only)
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            offres = offres.filter(heure_depart__date=date)
        except ValueError:
            pass

    # Gestion création demande via POST
    if request.method == 'POST':
        # On récupère les champs depuis le formulaire HTML (inputs non-Django)
        point_depart_demande = request.POST.get('point_depart_demande', '').strip()
        point_arrivee_demande = request.POST.get('point_arrivee_demande', '').strip()
        heure_souhaitee_str = request.POST.get('heure_souhaitee', '').strip()

        # Validation basique
        if point_depart_demande and point_arrivee_demande and heure_souhaitee_str:
            try:
                heure_souhaitee = parse_datetime(heure_souhaitee_str)
                if heure_souhaitee is None:
                    raise ValueError("Format datetime invalide")
                
                # Création de la demande liée au profil utilisateur
                DemandeCovoiturage.objects.create(
                    passager=request.user.profile,  # Assure-toi que le user a un profile
                    point_depart=point_depart_demande,
                    point_arrivee=point_arrivee_demande,
                    heure_souhaitee=heure_souhaitee,
                )
                return redirect('rechercher')  # redirection après création demande
            except Exception as e:
                error = f"Erreur lors de la création de la demande: {e}"
                # tu peux passer ce message à ton template pour l'afficher
        else:
            error = "Tous les champs de la demande doivent être remplis."

    else:
        error = None

    context = {
        'offres': offres,
        'filtres': {
            'point_depart': point_depart,
            'point_arrivee': point_arrivee,
            'date': date_str,
        },
        'error': error,
    }
    return render(request, 'APP/rechercher.html', context)


@login_required
def publier(request):
    if request.method == 'POST':
        point_depart = request.POST.get('point_depart')
        point_arrivee = request.POST.get('point_arrivee')
        heure_depart = request.POST.get('heure_depart')
        places_disponibles = request.POST.get('places_disponibles')
        description = request.POST.get('description')
        prix = request.POST.get('prix')

        # Vérification minimale
        if point_depart and point_arrivee and heure_depart and places_disponibles:
            try:
                offre = OffreCovoiturage.objects.create(
                    conducteur=request.user,
                    point_depart=point_depart,
                    point_arrivee=point_arrivee,
                    heure_depart=datetime.fromisoformat(heure_depart),  # ex: "2025-06-17T14:30"
                    places_disponibles=int(places_disponibles),
                    description=description,
                    prix=Decimal(prix) if prix else Decimal('200.00'),
                )
                return redirect('/')  # à adapter
            except Exception as e:
                print("Erreur de création :", e)  # Log temporaire

    return render(request, 'APP/publier.html')

@login_required
def profil(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('/profil/')  # Remplace par le nom de ton URL
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'APP/profil.html', {'form': form})

def inscription(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre compte a bien été créé ! Vous pouvez maintenant vous connecter.')
            return redirect('connexion')  # redirige vers la page de connexion (à adapter)
    else:
        form = UserRegisterForm()
    return render(request, 'APP/inscription.html', {'form': form})