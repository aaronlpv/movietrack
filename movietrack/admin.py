from django.contrib import admin
from .models import Genre, Movie, Event, Comment

# Registers models in the admin interface

admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(Event)
admin.site.register(Comment)