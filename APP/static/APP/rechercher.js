document.addEventListener('DOMContentLoaded', function() {
    // Éléments DOM
    const searchBtn = document.getElementById('search-btn');
    const clearFiltersBtn = document.getElementById('clear-filters');
    const applyFiltersBtn = document.getElementById('apply-filters');
    const initialState = document.getElementById('initial-state');
    const noResults = document.getElementById('no-results');
    const tripsList = document.getElementById('trips-list');
    const filtersHeader = document.getElementById('advanced-filters-header');
    const filtersContent = document.getElementById('advanced-filters');

    // Données de test
    const sampleTrips = [
        {
            id: 1,
            pointDepart: "Arconville",
            destination: "IFRI",
            date: "2025-06-20",
            heureDepart: "08:00",
            heureArrivee: "10:30",
            prix: 0,
            conducteur: "Jean D.",
            note: 4.5,
            places: 3,
            voiture: "Peugeot 308"
        },
        {
            id: 2,
            pointDepart: "IFRI",
            destination: "Tankpè",
            date: "2025-06-21",
            heureDepart: "14:00",
            heureArrivee: "17:30",
            prix: 0,
            conducteur: "Marie L.",
            note: 4.8,
            places: 1,
            moto: "TVS"
        }
    ];

    // Initialisation
    initDateInput();
    setupEventListeners();

    // Fonctions
    function initDateInput() {
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('date').value = today;
        document.getElementById('date').min = today;
    }

    function setupEventListeners() {
        searchBtn.addEventListener('click', performSearch);
        clearFiltersBtn.addEventListener('click', clearFilters);
        applyFiltersBtn.addEventListener('click', applyFilters);
        filtersHeader.addEventListener('click', toggleFilters);
    }

    function performSearch() {
        const departure = document.getElementById('departure').value.trim();
        const destination = document.getElementById('destination').value.trim();
        const date = document.getElementById('date').value;

        // Simulation de recherche
        let results = sampleTrips.filter(trip => {
            return (!departure || trip.pointDepart.toLowerCase().includes(departure.toLowerCase())) &&
                   (!destination || trip.destination.toLowerCase().includes(destination.toLowerCase())) &&
                   (!date || trip.date === date);
        });

        displayResults(results);
    }

    function displayResults(trips) {
        initialState.classList.add('hidden');
        noResults.classList.add('hidden');
        tripsList.classList.add('hidden');

        if (trips.length === 0) {
            noResults.classList.remove('hidden');
            return;
        }

        tripsList.innerHTML = '';
        trips.forEach(trip => {
            const tripElement = createTripCard(trip);
            tripsList.appendChild(tripElement);
        });

        tripsList.classList.remove('hidden');
    }

    function createTripCard(trip) {
        const card = document.createElement('div');
        card.className = 'trajet-card';
        card.innerHTML = `
            <div class="trajet-header">
                <div class="trajet-route">
                    <span class="depart">${trip.pointDepart}</span>
                    <span class="arrow">→</span>
                    <span class="arrivee">${trip.destination}</span>
                </div>
                <div class="trajet-prix">${trip.prix}Fcfa</div>
            </div>
            
            <div class="trajet-details">
                <div class="detail-item">
                    <span class="icon">📅</span>
                    <span>${formatDate(trip.date)}</span>
                </div>
                <div class="detail-item">
                    <span class="icon">🕐</span>
                    <span>${trip.heureDepart} - ${trip.heureArrivee}</span>
                </div>
                <div class="detail-item">
                    <span class="icon">👤</span>
                    <span>${trip.conducteur}</span>
                </div>
                <div class="detail-item">
                    <span class="icon">⭐</span>
                    <span>${trip.note}/5</span>
                </div>
                <div class="detail-item">
                    <span class="icon">💺</span>
                    <span>${trip.places} places</span>
                </div>
                <div class="detail-item">
                    <span class="icon">${trip.moto ? '🏍️' : '🚗'}</span>
                    <span>${trip.moto || trip.voiture}</span>
                </div>
            </div>

            
            
            <div class="trajet-actions">
                <button class="reserve-btn">Réserver</button>
                <button class="message-btn">Message</button>
            </div>
        `;

        // Ajouter les événements
        card.querySelector('.reserve-btn').addEventListener('click', () => handleReservation(trip.id));
        card.querySelector('.message-btn').addEventListener('click', () => handleMessage(trip));
        
        return card;
    }

    function formatDate(dateString) {
        const options = { weekday: 'long', day: 'numeric', month: 'long' };
        return new Date(dateString).toLocaleDateString('fr-FR', options);
    }

    function clearFilters() {
        document.getElementById('departure').value = '';
        document.getElementById('destination').value = '';
        document.getElementById('date').value = new Date().toISOString().split('T')[0];
        document.getElementById('max-price').value = '';
        document.getElementById('departure-time').value = '';
        document.getElementById('min-rating').value = '';

        initialState.classList.remove('hidden');
        noResults.classList.add('hidden');
        tripsList.classList.add('hidden');
    }

    function applyFilters() {
        performSearch();
    }

    function toggleFilters() {
        filtersContent.classList.toggle('hidden');
        const arrow = filtersHeader.querySelector('.arrow');
        arrow.textContent = arrow.textContent === '▼' ? '▲' : '▼';
    }

    function handleReservation(tripId) {
        const trip = sampleTrips.find(t => t.id === tripId);
        if (trip) {
            alert(`Réservation du trajet ${trip.pointDepart} → ${trip.destination}\nPrix: ${trip.prix}Fcfa\n\nConfirmez-vous la réservation ?`);
        }
    }


    
    function handleMessage(trip) {
        // Création de la modale de message
        const modal = document.createElement('div');
        modal.className = 'message-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>Envoyer un message à ${trip.conducteur}</h3>
                <textarea id="message-text" placeholder="Votre message..." rows="4"></textarea>
                <div class="modal-buttons">
                    <button class="cancel-btn">Annuler</button>
                    <button class="send-btn">Envoyer</button>
                </div>
            </div>
        `;
    
        document.body.appendChild(modal);
        
        // Activer la modale après un léger délai pour l'animation
        setTimeout(() => modal.classList.add('active'), 10);
    
        // Gestion des événements
        modal.querySelector('.cancel-btn').addEventListener('click', () => {
            modal.classList.remove('active');
            setTimeout(() => document.body.removeChild(modal), 300);
        });
    
        modal.querySelector('.send-btn').addEventListener('click', () => {
            const messageText = document.getElementById('message-text').value.trim();
            if (messageText) {
                // Ici vous pourriez envoyer le message à l'API
                console.log(`Message envoyé à ${trip.conducteur}:`, messageText);
                alert(`Message envoyé à ${trip.conducteur} !`);
                modal.classList.remove('active');
                setTimeout(() => document.body.removeChild(modal), 300);
            } else {
                alert('Veuillez écrire un message');
            }
        });
    }
});