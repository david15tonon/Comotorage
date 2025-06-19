from django.contrib import admin
from .models import OffreCovoiturage, DemandeCovoiturage, Matching, Profile

admin.site.register(OffreCovoiturage)
admin.site.register(DemandeCovoiturage)
admin.site.register(Matching)
admin.site.register(Profile)