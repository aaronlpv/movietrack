from django.urls import path
from . import views

urlpatterns = [
    path('movie-search/', views.movie_search, name='movie-search'),
    path('movie/', views.get_movie, name='movie'),
    path('favorite/', views.favorite, name='favorite'),
    path('want_to_watch/', views.want_to_watch, name='want-to-watch'),
    path('seen/', views.seen, name='seen'),
    path('friend/', views.friend, name='friend'),

    path('omdb-debug/', views.omdb_debug, name='omdb-debug')
]