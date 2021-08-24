"""webtech URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views

urlpatterns = [
    # Homepage
    path('', views.FilterableMovieList.as_view(), name='home'),

    # Movie lists
	path('moviesort/<slug:filter>/', views.FilterableMovieList.as_view(), name='home'),
	path('moviesort/<slug:extra>/<slug:filter>/', views.FilterableMovieList.as_view(), name='home'),
    path('user/<user_id>/seen/', views.SeenList.as_view(), name='seen'),
	path('user/<user_id>/seen/moviesort/<slug:filter>/', views.SeenList.as_view(), name='seen'),
	path('user/<user_id>/seen/moviesort/<slug:extra>/<slug:filter>/', views.SeenList.as_view(), name='seen'),
    path('user/<user_id>/want-to-watch/', views.WantToWatchList.as_view(), name='wtw'),
	path('user/<user_id>/want-to-watch/moviesort/<slug:filter>/', views.WantToWatchList.as_view(), name='wtw'),
	path('user/<user_id>/want-to-watch/moviesort/<slug:extra>/<slug:filter>/', views.WantToWatchList.as_view(), name='wtw'),

    # Movie related views
    path('movie/<pk>/', views.MovieDetail.as_view(), name='movie'),
    path('movie/<pk>/comment/', views.submit_comment, name='movie-comment'),
    path('movie/<pk>/edit/', views.EditMovie.as_view(), name='movie-edit'),
    path('create-movie/', views.CreateMovie.as_view(), name='movie-create'),
    path('import-movie/', views.OmdbFormView.as_view(), name='movie-import'),

    # User related views
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.Register.as_view(), name='register'),

    path('user/<pk>/profile/', views.UserProfile.as_view(), name='profile'),
    path('users/', views.UserList.as_view(), name='users'),
    path('edit-profile/', views.ProfileEdit.as_view(), name='profile-edit'),
    path('user/<pk>/friends/', views.FriendList.as_view(), name='friends'),

    # Event related views
    path('events/', views.EventList.as_view(), name='events'),
    path('events/add', views.add_event, name='events-add'),
    path('events/<event_id>/delete', views.delete_event, name='events-delete'),
    path('events/<event_id>/participate/<user_id>', views.participate_event, name='events-participate'),
    path('events/<event_id>/unparticipate/<user_id>', views.unparticipate_event, name='events-unparticipate')
]
