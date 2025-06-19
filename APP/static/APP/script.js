// À ajouter dans le <head>
<script src="https://maps.googleapis.com/maps/api/js?key=VOTRE_CLE_API&callback=initMap" async defer></script>

// Script d'initialisation
function initMap() {
    const map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 48.8566, lng: 2.3522 }, // Paris par défaut
        zoom: 6
    });
    
    // Ajouter vos trajets comme marqueurs ou polylines
}









