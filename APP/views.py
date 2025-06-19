from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UserRegisterForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import OffreCovoiturage, DemandeCovoiturage, Matching
from .models import Profile
from .forms import ProfileForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse, NoReverseMatch
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from decimal import Decimal
from datetime import datetime
from django.utils.dateparse import parse_datetime
import json

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
    offres = OffreCovoiturage.objects.filter(places_disponibles__gt=0)
    demande_creee = None
    matching_disponible = False

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
                profile, created = Profile.objects.get_or_create(user=request.user)
                demande_creee = DemandeCovoiturage.objects.create(
                    passager=profile,
                    point_depart=point_depart_demande,
                    point_arrivee=point_arrivee_demande,
                    heure_souhaitee=heure_souhaitee,
                )
                
                # Géocoder automatiquement les adresses (optionnel)
                try:
                    from .matching import MatchingAlgorithm
                    matcher = MatchingAlgorithm()
                    coords_depart = matcher.get_coordinates(point_depart_demande)
                    coords_arrivee = matcher.get_coordinates(point_arrivee_demande)
                    
                    demande_creee.latitude_depart = coords_depart[0]
                    demande_creee.longitude_depart = coords_depart[1]
                    demande_creee.latitude_arrivee = coords_arrivee[0]
                    demande_creee.longitude_arrivee = coords_arrivee[1]
                    demande_creee.save()
                except Exception as e:
                    print(f"Erreur géocodage: {e}")
                
                matching_disponible = True
                messages.success(request, "Demande créée avec succès ! Vous pouvez maintenant chercher des matches.")
                
            except Exception as e:
                messages.error(request, f"Erreur lors de la création de la demande: {e}")
        else:
            messages.error(request, "Tous les champs de la demande doivent être remplis.")

    context = {
        'offres': offres,
        'demande_creee': demande_creee,
        'matching_disponible': matching_disponible,
        'filtres': {
            'point_depart': point_depart,
            'point_arrivee': point_arrivee,
            'date': date_str,
        }
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
                
                # Géocoder automatiquement les adresses (optionnel)
                try:
                    from .matching import MatchingAlgorithm
                    matcher = MatchingAlgorithm()
                    coords_depart = matcher.get_coordinates(point_depart)
                    coords_arrivee = matcher.get_coordinates(point_arrivee)
                    
                    offre.latitude_depart = coords_depart[0]
                    offre.longitude_depart = coords_depart[1]
                    offre.latitude_arrivee = coords_arrivee[0]
                    offre.longitude_arrivee = coords_arrivee[1]
                    offre.save()
                except Exception as e:
                    print(f"Erreur géocodage: {e}")
                
                messages.success(request, "Offre publiée avec succès !")
                return redirect('/')
            except Exception as e:
                print("Erreur de création :", e)
                messages.error(request, f"Erreur lors de la création de l'offre: {e}")

    return render(request, 'APP/publier.html')

@login_required
def profil(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('/profil/')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'APP/profil.html', {'form': form})

def inscription(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre compte a bien été créé ! Vous pouvez maintenant vous connecter.')
            return redirect('connexion')
    else:
        form = UserRegisterForm()
    return render(request, 'APP/inscription.html', {'form': form})

# ========== NOUVELLES VUES POUR LE MATCHING ==========

@login_required
@require_http_methods(["POST"])
def run_matching(request):
    """API pour lancer l'algorithme de matching"""
    try:
        data = json.loads(request.body)
        demande_id = data.get('demande_id')
        min_score = data.get('min_score', 30)
        
        if not demande_id:
            return JsonResponse({'error': 'ID de demande requis'}, status=400)
        
        demande = get_object_or_404(DemandeCovoiturage, id=demande_id)
        
        # Vérifier que l'utilisateur peut accéder à cette demande
        if demande.passager.user != request.user:
            return JsonResponse({'error': 'Accès non autorisé'}, status=403)
        
        try:
            from .matching import MatchingAlgorithm
            matcher = MatchingAlgorithm()
            matches = matcher.find_matches(demande, min_score)
        except ImportError:
            # Si l'algorithme n'est pas encore implémenté, simulation basique
            offres = OffreCovoiturage.objects.filter(
                places_disponibles__gt=0,
                point_depart__icontains=demande.point_depart[:3]
            )[:5]
            
            matches = []
            for offre in offres:
                matches.append({
                    'offre': offre,
                    'score': 75.0,  # Score simulé
                    'distance_depart': 2.5,  # Distance simulée
                    'distance_arrivee': 1.8   # Distance simulée
                })
        
        # Convertir en format JSON
        results = []
        for match in matches[:10]:
            offre = match['offre']
            results.append({
                'offre_id': offre.id,
                'conducteur': offre.conducteur.get_full_name(),
                'point_depart': offre.point_depart,
                'point_arrivee': offre.point_arrivee,
                'heure_depart': offre.heure_depart.isoformat(),
                'places_disponibles': offre.places_disponibles,
                'prix': float(offre.prix),
                'score': round(match['score'], 1),
                'distance_depart': round(match['distance_depart'], 2),
                'distance_arrivee': round(match['distance_arrivee'], 2),
                'description': offre.description or ''
            })
        
        return JsonResponse({
            'success': True,
            'matches': results,
            'total': len(results)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def matching_results(request):
    """Page d'affichage des résultats de matching"""
    demande_id = request.GET.get('demande_id')
    
    if not demande_id:
        messages.error(request, 'ID de demande manquant')
        return redirect('rechercher')
    
    try:
        demande = get_object_or_404(DemandeCovoiturage, id=demande_id)
        
        if demande.passager.user != request.user:
            messages.error(request, 'Accès non autorisé')
            return redirect('rechercher')
        
        try:
            from .matching import MatchingAlgorithm
            matcher = MatchingAlgorithm()
            matches = matcher.find_matches(demande)
        except ImportError:
            # Simulation basique si l'algorithme n'est pas encore implémenté
            offres = OffreCovoiturage.objects.filter(
                places_disponibles__gt=0,
                point_depart__icontains=demande.point_depart[:3]
            )
            
            matches = []
            for offre in offres:
                matches.append({
                    'offre': offre,
                    'score': 75.0,
                    'distance_depart': 2.5,
                    'distance_arrivee': 1.8
                })
        
        # Pagination
        paginator = Paginator(matches, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'APP/matching_results.html', {
            'demande': demande,
            'matches': page_obj,
            'total_matches': len(matches)
        })
        
    except Exception as e:
        messages.error(request, f'Erreur: {str(e)}')
        return redirect('rechercher')

@login_required
@require_http_methods(["POST"])
def create_matching(request):
    """Créer un matching entre une offre et une demande"""
    try:
        data = json.loads(request.body)
        offre_id = data.get('offre_id')
        demande_id = data.get('demande_id')
        
        if not offre_id or not demande_id:
            return JsonResponse({'error': 'IDs requis'}, status=400)
        
        offre = get_object_or_404(OffreCovoiturage, id=offre_id)
        demande = get_object_or_404(DemandeCovoiturage, id=demande_id)
        
        # Vérifications de sécurité
        if demande.passager.user != request.user:
            return JsonResponse({'error': 'Accès non autorisé'}, status=403)
        
        if offre.places_disponibles <= 0:
            return JsonResponse({'error': 'Aucune place disponible'}, status=400)
        
        # Calculer le score et créer le matching
        try:
            from .matching import MatchingAlgorithm
            matcher = MatchingAlgorithm()
            score = matcher.calculate_compatibility_score(offre, demande)
            matching, created = matcher.create_matching(offre, demande, score)
        except ImportError:
            # Création simple si l'algorithme n'est pas implémenté
            matching, created = Matching.objects.get_or_create(
                offre=offre,
                demande=demande,
                defaults={'score_compatibilite': 75.0}
            )
        
        if created:
            # Réduire le nombre de places disponibles
            offre.places_disponibles -= 1
            offre.save()
            
            # Mettre à jour le statut de la demande si le champ existe
            try:
                demande.statut = 'matched'
                demande.save()
            except:
                pass  # Si le champ statut n'existe pas encore
        
        return JsonResponse({
            'success': True,
            'matching_id': matching.id,
            'created': created,
            'message': 'Matching créé avec succès' if created else 'Matching déjà existant'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def geocode_address(request):
    """API pour géocoder une adresse"""
    try:
        data = json.loads(request.body)
        address = data.get('address')
        
        if not address:
            return JsonResponse({'error': 'Adresse requise'}, status=400)
        
        try:
            from .matching import MatchingAlgorithm
            matcher = MatchingAlgorithm()
            coords = matcher.get_coordinates(address)
        except ImportError:
            # Coordonnées par défaut (Cotonou, Bénin)
            coords = (6.3703, 2.3912)
        
        return JsonResponse({
            'success': True,
            'latitude': coords[0],
            'longitude': coords[1],
            'address': address
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)