

from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.index, name = 'index'),
    path('accueil/', views.accueil, name = 'accueil'),
    path('publier/', views.publier, name = 'publier'),
    path('rechercher/', views.rechercher, name = 'rechercher'),
    path('inscription/', views.inscription, name = 'inscription'),
    path('connexion/', views.connexion, name = 'connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('profil/', views.profil, name='deconnexion'),
    path('matching/run/', views.run_matching, name='run_matching'),
    path('matching/results/', views.matching_results, name='matching_results'),
    path('matching/create/', views.create_matching, name='create_matching'),
    path('api/geocode/', views.geocode_address, name='geocode_address'),
]

