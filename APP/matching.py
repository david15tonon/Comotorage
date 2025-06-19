import math
from datetime import timedelta
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class MatchingAlgorithm:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="drive_me")
        
    def get_coordinates(self, address):
        """Obtient les coordonnées géographiques d'une adresse"""
        cache_key = f"geocode_{address.lower().replace(' ', '_')}"
        coords = cache.get(cache_key)
        
        if coords is None:
            try:
                location = self.geolocator.geocode(address)
                if location:
                    coords = (location.latitude, location.longitude)
                    cache.set(cache_key, coords, 86400)  # Cache 24h
                else:
                    coords = (0, 0)  # Coordonnées par défaut
            except Exception as e:
                logger.error(f"Erreur géocodage pour {address}: {e}")
                coords = (0, 0)
                
        return coords
    
    def calculate_distance(self, coord1, coord2):
        """Calcule la distance en km entre deux points"""
        try:
            return geodesic(coord1, coord2).kilometers
        except:
            return float('inf')
    
    def calculate_time_compatibility(self, heure_offre, heure_demande):
        """Calcule la compatibilité horaire (0-1)"""
        diff = abs((heure_offre - heure_demande).total_seconds())
        # Tolérance de 2 heures = score maximum
        tolerance_seconds = 2 * 3600  # 2 heures
        
        if diff <= tolerance_seconds:
            return 1.0 - (diff / (2 * tolerance_seconds))
        else:
            return max(0, 1.0 - (diff / (4 * tolerance_seconds)))
    
    def calculate_compatibility_score(self, offre, demande):
        """Calcule le score de compatibilité global (0-100)"""
        # Coordonnées des points
        depart_offre = self.get_coordinates(offre.point_depart)
        arrivee_offre = self.get_coordinates(offre.point_arrivee)
        depart_demande = self.get_coordinates(demande.point_depart)
        arrivee_demande = self.get_coordinates(demande.point_arrivee)
        
        # Distances (en km)
        dist_depart = self.calculate_distance(depart_offre, depart_demande)
        dist_arrivee = self.calculate_distance(arrivee_offre, arrivee_demande)
        
        # Score de proximité géographique (50% du score total)
        max_distance = 5.0  # 5km de tolérance
        score_depart = max(0, 1 - (dist_depart / max_distance))
        score_arrivee = max(0, 1 - (dist_arrivee / max_distance))
        score_geo = (score_depart + score_arrivee) / 2
        
        # Score de compatibilité horaire (30% du score total)
        score_temps = self.calculate_time_compatibility(
            offre.heure_depart, 
            demande.heure_souhaitee
        )
        
        # Score de disponibilité (20% du score total)
        score_places = 1.0 if offre.places_disponibles > 0 else 0.0
        
        # Score final pondéré
        score_final = (
            score_geo * 0.5 +
            score_temps * 0.3 +
            score_places * 0.2
        ) * 100
        
        return min(100, max(0, score_final))
    
    def find_matches(self, demande, min_score=30):
        """Trouve les offres compatibles pour une demande"""
        from APP.models import OffreCovoiturage, Matching
        
        # Offres disponibles (non expirées, avec places)
        offres = OffreCovoiturage.objects.filter(
            places_disponibles__gt=0,
            heure_depart__gte=demande.heure_souhaitee - timedelta(hours=4)
        ).exclude(
            # Exclure les offres déjà matchées avec cette demande
            matching__demande=demande
        )
        
        matches = []
        
        for offre in offres:
            score = self.calculate_compatibility_score(offre, demande)
            
            if score >= min_score:
                matches.append({
                    'offre': offre,
                    'demande': demande,
                    'score': score,
                    'distance_depart': self.calculate_distance(
                        self.get_coordinates(offre.point_depart),
                        self.get_coordinates(demande.point_depart)
                    ),
                    'distance_arrivee': self.calculate_distance(
                        self.get_coordinates(offre.point_arrivee),
                        self.get_coordinates(demande.point_arrivee)
                    )
                })
        
        # Trier par score décroissant
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches
    
    def create_matching(self, offre, demande, score):
        """Crée un matching en base de données"""
        from APP.models import Matching
        
        matching, created = Matching.objects.get_or_create(
            offre=offre,
            demande=demande,
            defaults={'score_compatibilite': score}
        )
        
        return matching, created