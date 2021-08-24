from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django import template
from django.conf import settings
from django.db import connection

from movietrack.validators import validate_year, validate_score, validate_runtime


# A genre is just a primary key and a name.
# We could also store movie genres as enums but doing it like this
# allows us to dynamically add genres from OMDB and
# rename genres through the admin interface.
class Genre(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    year = models.IntegerField(validators=[validate_year])
    runtime = models.IntegerField(help_text='in minutes', validators=[validate_runtime])
    poster = models.ImageField(upload_to='posters/')
    genres = models.ManyToManyField(Genre,help_text='(hold Ctrl key for multiple select)')

    def __str__(self):
        return f'{self.title} ({self.year})'

    def get_absolute_url(self):
        return reverse('movie', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['title', 'year']


# each of the valid ratings for movies and their description
ratings = {
    10: '(10) Masterpiece',
    9: '(9) Great',
    8: '(8) Very good',
    7: '(7) Good',
    6: '(6) Fine',
    5: '(5) Average',
    4: '(4) Bad',
    3: '(3) Very bad',
    2: '(2) Horrible',
    1: '(1) Appalling',
}

# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
# This model links our application-specific info to
# the django.contrib.auth User model.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    friends = models.ManyToManyField('self', symmetrical=True)
    seen = models.ManyToManyField(Movie, through='MovieRating', related_name='users_seen', through_fields=('user', 'movie'))
    want_to_watch = models.ManyToManyField(Movie, related_name='users_wtw')
    favorites = models.ManyToManyField(Movie, related_name='users_favorited')

    def get_profile_pic(self):
        if self.profile_picture:
            return self.profile_picture.url
        else:
            return settings.STATIC_URL + 'user-placeholder.png'

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('profile',  kwargs={'pk': self.pk})


# The following functions create a profile for each newly created user.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


affinity_query = 'SELECT SUM(ABS(m1.rating - m2.rating)) / COUNT(*), COUNT(*) FROM movietrack_movierating m1, movietrack_movierating m2 ON m1.movie_id = m2.movie_id WHERE m1.user_id = %s AND m2.user_id=%s AND m1.rating IS NOT NULL AND m2.rating IS NOT NULL;'

# The MovieRating model stores what movies a user has seen and
# how he rated them. The rating is optional.
class MovieRating(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[validate_score], null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    # We can calculate an 'affinity score' between users based
    # on the average distance between their ratings for every movie
    # they both have rated.
    # Unfortunately this kind of thing is extremely hard / impossible
    # to do with Django's ORM so we have to resort to raw SQL here.
    def get_affinity(user1, user2):
        with connection.cursor() as cursor:
            cursor.execute(affinity_query, [user1.id, user2.id])
            results = cursor.fetchone()
            common = results[1]
            affinity_raw = results[0] or 0
            affinity = 10 - affinity_raw
        return (common, affinity)

    class Meta:
        unique_together = (('user', 'movie'))
        ordering = ['rating']

# This model stores one comment on a movie
class Comment(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='authored_comments')
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'[{self.timestamp}] <{self.author}> {self.body}'


class FriendRequest(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friendrequests_sent')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friendrequests_received')
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('sender', 'receiver'))


class Event(models.Model):
    title = models.CharField(max_length = 100)
    date = models.DateField()
    time = models.TimeField()
    streetname = models.CharField(max_length = 100)
    streetnumber = models.CharField(max_length = 50)
    zipcode = models.CharField(max_length = 10)
    city = models.CharField(max_length = 100)
    country = models.CharField(max_length = 100)
    movies = models.CharField(max_length = 200)
    maxlimit = models.CharField(max_length = 4)
    users = models.ManyToManyField(User)

    def __str__(self):
       	return self.title
