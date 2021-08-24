from django.core import files
from io import BytesIO
import json
import urllib.request as urllib

from movietrack.models import Movie, Genre

# IMDB movie IDs all start by 'tt' followed by 7 digits
imdb_id_re = r'tt\d{7}'
api_url = 'https://www.omdbapi.com/?apikey=6c626690&i='

# Loads a movie from OMDB and saves it to the database
# Takes an IMDB movie ID as param
# Returns the primary key of the created movie
def import_from_omdb(id):
    result = urllib.urlopen(api_url + id).read()
    res_json = json.loads(result)

    title = res_json['Title']
    year = res_json['Year']
    description = res_json['Plot']
    # runtime format example: "100 min"
    runtime = int(res_json['Runtime'].split()[0])
    # get or create each of the genres of this movie
    genres = [Genre.objects.get_or_create(name=g.strip())[0] for g in res_json['Genre'].split(', ')]
    poster_url = res_json['Poster']

    # save poster to memory
    res_img = urllib.urlopen(poster_url).read()
    fp = BytesIO()
    fp.write(res_img)
    
    new_movie = Movie.objects.create(
        title=title,
        year=year,
        runtime=runtime,
        description=description,
    )
    new_movie.genres.set(genres)
    new_movie.poster.save('poster', files.File(fp))

    return new_movie.pk