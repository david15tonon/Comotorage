document.addEventListener('DOMContentLoaded', function() {
    // Initialisation de la date/heure
    const now = new Date();
    const datetimeInput = document.getElementById('datetime-input');
    
    // Format YYYY-MM-DDTHH:MM
    datetimeInput.value = now.toISOString().slice(0, 16);
    
    // Gestion de la soumission du formulaire
    const publishBtn = document.getElementById('continue-btn');
    publishBtn.addEventListener('click', function(e) {
        e.preventDefault();
        publishTrip();
    });
    
    // Fonction de publication
    function publishTrip() {
        // Récupération des valeurs
        const departure = document.getElementById('departure').value.trim();
        const destination = document.getElementById('destination').value.trim();
        const datetime = document.getElementById('datetime-input').value;
        const seats = document.getElementById('seats-select').value;
        const price = document.getElementById('price').value;
        const description = document.getElementById('description').value.trim();
        
        // Validation simple
        if (!departure || !destination) {
            alert('Veuillez renseigner le point de départ et la destination');
            return;
        }
        
        // Formatage de la date
        const formattedDate = formatDateTime(datetime);
        
        // Création de l'objet trajet
        const trip = {
            departure,
            destination,
            datetime: formattedDate,
            seats,
            price: price || '0',
            description: description || 'Aucune description'
        };
        
        // Envoi des données (simulation)
        console.log('Trajet à publier:', trip);
        
        // Feedback utilisateur
        alert(`Trajet publié avec succès !\n\nDe: ${departure}\nÀ: ${destination}\nLe: ${formattedDate}`);
        
        // Réinitialisation du formulaire
        resetForm();
    }
    
    // Formatage de la date
    function formatDateTime(datetimeString) {
        if (!datetimeString) return 'Non spécifié';
        
        const date = new Date(datetimeString);
        return date.toLocaleDateString('fr-FR', {
            weekday: 'long',
            day: 'numeric',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    // Réinitialisation du formulaire
    function resetForm() {
        document.getElementById('departure').value = '';
        document.getElementById('destination').value = '';
        document.getElementById('seats-select').value = '1';
        document.getElementById('price').value = '0';
        document.getElementById('description').value = '';
        
        // Réinitialiser la date/heure à maintenant
        const now = new Date();
        document.getElementById('datetime-input').value = now.toISOString().slice(0, 16);
    }
});