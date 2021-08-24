import datetime
import re

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core import serializers
from django.db.models import Avg, Sum
from django.http import (Http404, HttpResponse, HttpResponseForbidden,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404, render
from django.urls import resolve, reverse, reverse_lazy
from django.views.generic import (CreateView, DetailView, FormView, ListView,
                                  UpdateView)
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin

import api.omdb as omdb

from .models import (Comment, Event, FriendRequest, Genre, Movie, MovieRating,
                     Profile, ratings)

# This file contains all the HTML views

# Form to import movies from OMDB
class OmdbForm(forms.Form):
    movie = forms.CharField(label="IMDB ID or URL")

    def clean_movie(self):
        # extract the IMDB ID from the field or return error
        # if none is found
        data = self.cleaned_data['movie']
        match = re.search(omdb.imdb_id_re, data)
        if match:
            return match.group()
        else:
            raise forms.ValidationError("Not a valid IMDB URL or ID.")

# View for importing movies from OMDB
class OmdbFormView(FormView):
    template_name = 'movie_import.html'
    form_class = OmdbForm

    def get_success_url(self):
        if self.new_movie:
            return reverse('movie', kwargs={'pk': self.new_movie})
        else:
            return reverse('home')

    def form_valid(self, form):
        try:
            self.new_movie = omdb.import_from_omdb(form.cleaned_data['movie'])
        except:
            pass
        return super().form_valid(self)

# User profile, shows bio, profile picture, friends, favorites and some stats
class UserProfile(DetailView):
    model = Profile
    context_object_name = 'profile'
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # calculate total time watched
        mins = MovieRating.objects.filter(user = self.object).select_related().aggregate(Sum('movie__runtime'))['movie__runtime__sum'] or 0
        context['days_watched'] = mins / (60 * 24)
        # if not the users own profile
        if user.is_authenticated and user.profile is not self.object:
            # calculate affinity between users
            common, affinity = MovieRating.get_affinity(user.profile, self.object)
            context['affinity'] = affinity
            context['common'] = common
            sender = user.profile
            # show friendship status
            receiver = self.object
            context['friendship_pending'] = FriendRequest.objects.filter(sender=sender, receiver=receiver).exists()
            context['friend'] = sender.friends.filter(id=receiver.pk).exists()
        return context

# Friendlist: show incoming and outgoing requests and current friends
class FriendList(DetailView):
    model = Profile
    context_object_name = 'profile'
    template_name = 'friend_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['friends'] = self.object.friends.all()
        current_user = self.request.user
        displayed_user = self.object.user
        if current_user.is_authenticated and current_user == displayed_user:
            user = self.object
            context['outg_requests'] = FriendRequest.objects.filter(sender=user).all()
            context['inc_requests'] = FriendRequest.objects.filter(receiver=user).all()
        return context

# Generic movie list
class MovieList(ListView):
    model = Movie
    context_object_name = 'movies'
    template_name = 'movie_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
		# used to make the seen overlay in the movielist
        user = self.request.user
        if user.is_authenticated:
            context['seen'] = user.profile.seen.all()
        return context


def get_user_or_404(id):
    return get_object_or_404(User, pk=id)
	
# returning the whole list or a sorted one
def sort(kwargs,list):
	# the url without filter means no sort is needed
    if 'filter' in kwargs:
		# the extra gives a genre on wich we need to filter, 
		# the others give a key on wich we need to sort
        if 'extra' in kwargs:
            return list.filter(genres__name = kwargs['filter'])
        else:
		# just using movierating as key to order on would put in 
		# duplicates with all the ratings seperated
	
            if 'movierating' in kwargs['filter']:
			    #first we calculate the average
                def avg(mov):
                    user_ratings = MovieRating.objects.filter(movie=mov).exclude(rating__isnull=True)
                    avg = user_ratings.aggregate(Avg('rating'))['rating__avg']
                    return 0 if avg is None else avg
                lst = [(x,avg(x))for x in list.all()]
				#we sort using average and then only output the movie
                lst.sort(key=lambda tup: tup[1],reverse=True if '-' in kwargs['filter'] else False )		
                return [x[0] for x in lst]
				#ordering using year
            else:
                return list.order_by(kwargs['filter'])
    else:
        return list.all()
		
# Homepage shows all the movies, possibly sorted with sort function
class FilterableMovieList(MovieList):
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query is None:
            return sort(self.kwargs, Movie.objects)
        else:
            return Movie.objects.filter(title__istartswith=query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        return context

# all the movies in the watchlist corresponding to the current profile, possibly sorted
class WantToWatchList(MovieList):
    def get_queryset(self):
        profile = get_user_or_404(self.kwargs['user_id']).profile
        return sort(self.kwargs, profile.want_to_watch)
		
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_user_or_404(self.kwargs['user_id'])
        context['title'] = f'{user.username}\'s watchlist'
        return context
		
# all the seen movies corresponding to the current profile, possibly sorted
class SeenList(MovieList):
    def get_queryset(self):
        profile = get_user_or_404(self.kwargs['user_id']).profile
        return sort(self.kwargs, profile.seen)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_user_or_404(self.kwargs['user_id'])
        context['title'] = f'{user.username}\'s seenlist'
        return context

class MovieDetail(DetailView):
    model = Movie
    context_object_name = 'movie'
    template_name = 'movie_detail.html'

    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs)
        user = self.request.user
        movie = self.object
        context['ratings'] = ratings
        user_ratings = MovieRating.objects.filter(movie=movie).exclude(rating__isnull=True)
        context['average_score'] = user_ratings.aggregate(Avg('rating'))['rating__avg']
        context['score_users'] = user_ratings.count()
        context['comments'] = Comment.objects.filter(movie=movie)
        if user.is_authenticated:
            user = user.profile
            context['favorited'] = user.favorites.filter(pk=movie.pk).exists()
            context['wtw'] = user.want_to_watch.filter(pk=movie.pk).exists()
            try:
                score = MovieRating.objects.get(movie=movie, user=user).rating
                seen = True
            except MovieRating.DoesNotExist:
                seen = False
            context['seen'] = seen
            context['score'] = ratings[score] if seen and score else None
        return context

class EventList(ListView):
    model = Event
    context_object_name = "events"
    template_name = "event_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movies'] = Movie.objects.all()
        return context

    def get_queryset(self):
        return Event.objects.filter(date__gte=datetime.date.today()).order_by('date', 'time')


@login_required
def add_event(request):

    title = request.POST.get('title')

    if title is None or title is '':
        raise Http404

    events = Event.objects.create(
        title          = title,
        date           = request.POST.get('date'),
        time           = request.POST.get('time'),
        streetname     = request.POST.get('streetname'),
        streetnumber   = request.POST.get('streetnumber'),
        zipcode        = request.POST.get('zipcode'),
        city           = request.POST.get('city'),
        country        = request.POST.get('country'),
        movies         = request.POST.get('moviename'),
        maxlimit       = request.POST.get('maxlimit')
    )
    
    return HttpResponseRedirect(reverse('events'))

@login_required
def delete_event(request, event_id):

    event = Event.objects.get(id=event_id)
    event.delete()
    
    return HttpResponseRedirect(reverse('events'))

@login_required
def participate_event(request, event_id, user_id):
    event = Event.objects.get(id=event_id)

    if event.users.count() < int(event.maxlimit):
        user = User.objects.get(id=user_id)
        event.users.add(user)

    return HttpResponseRedirect(reverse('events'))
    

@login_required
def unparticipate_event(request, event_id, user_id):
    event = Event.objects.get(id=event_id)
    user = User.objects.get(id=user_id)
    event.users.remove(user)

    return HttpResponseRedirect(reverse('events'))
    


# Allows users to submit comments on the movie detail view
# Would be cleaner to add a FormMixin to the movie detail view directly
# but this works and is shorter
@login_required
def submit_comment(request, pk):
    body = request.POST.get('comment')
    # empty body not allowed
    if body is None or body is '':
        raise Http404
    movie = get_object_or_404(Movie, pk=pk)
    comment = Comment.objects.create(
        movie=movie,
        author=request.user.profile,
        body=body,
    )
    # redirect to the movie page the comment was posted from
    return HttpResponseRedirect(reverse('movie',  kwargs={'pk': movie.id}))

# Allows users to upload a profile picture and edit their bio
class ProfileEdit(LoginRequiredMixin, UpdateView):
    models = Profile
    fields = ['bio', 'profile_picture']
    template_name = 'profile_edit.html'

    def get_object(self):
        return self.request.user.profile

# Allows uers to create new movies
class CreateMovie(LoginRequiredMixin, CreateView):
    model = Movie
    fields = ['title', 'year', 'description', 'runtime', 'poster', 'genres']
    template_name = "movie_create.html"

# Allows users to modify existing movie info
class EditMovie(LoginRequiredMixin, UpdateView):
    model = Movie
    fields = ['title', 'year', 'description', 'runtime', 'poster', 'genres']
    template_name = "movie_edit.html"

# Registers new users
class Register(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'

# Shows a list of users, allows searching
class UserList(ListView):
    model = Profile
    context_object_name = 'users'
    template_name = 'user_list.html'

    def get_queryset(self):
        self.query = self.request.GET.get('q')
        if self.query is None:
            return Profile.objects.all()
        else:
            return Profile.objects.select_related().filter(user__username__istartswith=self.query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.query
        return context
