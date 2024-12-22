from django.urls import path
from .views import search_players

# Removed the search_page route

urlpatterns = [
    path('players/', search_players, name='search_players'),
]
