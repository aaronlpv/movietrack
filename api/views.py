from django.contrib.auth.models import User
from django.urls import reverse

import api.omdb as omdb
from api.json_response import (json_404, json_bad_method, json_bad_request,
                               json_ok, login_required, require_GET,
                               require_POST)
from movietrack.models import FriendRequest, Genre, Movie, MovieRating
from movietrack.validators import validate_score

# Allows users to search for movies
# Returns 5 results with their id, title, url and poster
# Is also used by the AJAX movie search
@require_GET
def movie_search(request):
    title = request.GET.get('q')
    if title is None or title.strip() is '':
        return json_bad_request()
    else:
        title = title.strip()
        suggestions = Movie.objects.filter(title__istartswith=title)[:5]
        response = [{'id': m.pk, 'title': str(m), 'url': reverse('movie', args=(m.pk,)), 'poster': m.poster.url} for m in suggestions]
        return json_ok({'results': response}, safe=False)

top250 = ['tt2582802', 'tt0111161', 'tt0068646', 'tt0071562', 'tt0468569', 'tt0050083', 'tt0108052', 'tt0167260', 'tt0110912', 'tt0060196', 'tt0137523', 'tt0120737', 'tt0109830', 'tt0080684', 'tt1375666', 'tt0167261', 'tt0073486', 'tt0099685', 'tt0133093', 'tt0047478', 'tt0317248', 'tt0114369', 'tt0076759', 'tt0102926', 'tt0038650', 'tt0118799', 'tt0114814', 'tt0245429', 'tt0120815', 'tt0110413', 'tt0120689', 'tt0816692', 'tt0054215', 'tt0120586', 'tt0021749', 'tt0064116', 'tt0034583', 'tt0027977', 'tt1675434', 'tt0253474', 'tt0407887', 'tt0103064', 'tt0088763', 'tt0047396', 'tt0082971', 'tt0172495', 'tt0110357', 'tt0482571', 'tt0078788', 'tt0209144', 'tt0078748', 'tt4154756', 'tt0032553', 'tt0095765', 'tt0095327', 'tt0043014', 'tt0405094', 'tt0057012', 'tt0050825', 'tt0081505', 'tt1853728', 'tt0910970', 'tt0119698', 'tt0051201', 'tt0169547', 'tt1345836', 'tt0364569', 'tt0090605', 'tt2380307', 'tt0087843', 'tt0082096', 'tt0033467', 'tt0112573', 'tt0052357', 'tt0053125', 'tt0105236', 'tt0086190', 'tt0022100', 'tt5311514', 'tt5074352', 'tt0180093', 'tt0086879', 'tt0986264', 'tt0056172', 'tt0338013', 'tt0066921', 'tt0211915', 'tt1187043', 'tt0062622', 'tt0036775', 'tt0114709', 'tt0075314', 'tt0045152', 'tt0093058', 'tt0361748', 'tt0040522', 'tt0056592', 'tt0012349', 'tt0070735', 'tt0435761', 'tt0119217', 'tt2106476', 'tt0208092', 'tt0086250', 'tt0071853', 'tt0059578', 'tt0053604', 'tt0119488', 'tt0017136', 'tt1832382', 'tt0097576', 'tt0042876', 'tt1049413', 'tt0042192', 'tt0055630', 'tt0372784', 'tt0053291', 'tt0105695', 'tt0363163', 'tt0040897', 'tt0095016', 'tt0113277', 'tt0044741', 'tt1727824', 'tt0081398', 'tt1255953', 'tt0057115', 'tt0118849', 'tt0476735', 'tt0457430', 'tt0071315', 'tt0041959', 'tt0096283', 'tt0089881', 'tt0347149', 'tt0055031', 'tt1305806', 'tt0015864', 'tt0050212', 'tt5027774', 'tt0268978', 'tt0120735', 'tt0047296', 'tt0112641', 'tt0050976', 'tt2096673', 'tt0080678', 'tt3170832', 'tt0031679', 'tt0993846', 'tt0434409', 'tt1291584', 'tt0083658', 'tt0017925', 'tt0050986', 'tt0046912', 'tt0117951', 'tt0477348', 'tt0469494', 'tt0167404', 'tt0031381', 'tt0084787', 'tt0116282', 'tt1205489', 'tt0077416', 'tt0266543', 'tt0091251', 'tt0015324', 'tt0118715', 'tt1130884', 'tt0266697', 'tt0061512', 'tt0032976', 'tt0046438', 'tt0978762', 'tt2119532', 'tt0018455', 'tt2267998', 'tt0892769', 'tt3011894', 'tt0107290', 'tt0758758', 'tt0079470', 'tt0116231', 'tt0025316', 'tt0107207', 'tt0091763', 'tt2278388', 'tt0092005', 'tt0120382', 'tt0074958', 'tt0079944', 'tt0395169', 'tt1517451', 'tt0060827', 'tt0052618', 'tt0353969', 'tt2024544', 'tt0405159', 'tt0046268', 'tt0019254', 'tt0060107', 'tt1979320', 'tt0405508', 'tt0112471', 'tt1392190', 'tt0053198', 'tt1895587', 'tt1392214', 'tt1028532', 'tt3315342', 'tt0245712', 'tt0093779', 'tt0264464', 'tt0087544', 'tt0064115', 'tt1201607', 'tt0075148', 'tt0072684', 'tt0198781', 'tt0032551', 'tt0033870', 'tt0246578', 'tt0046911', 'tt0088247', 'tt0097165', 'tt0083987', 'tt0113247', 'tt0056443', 'tt0107048', 'tt0050783', 'tt0032138', 'tt0073195', 'tt1856101', 'tt3783958', 'tt1454029', 'tt0118694', 'tt0070510', 'tt1954470', 'tt2991224', 'tt0381681', 'tt4016934', 'tt0087884', 'tt0036868', 'tt2015381', 'tt0440963', 'tt0325980', 'tt0092067', 'tt4430212', 'tt0056801']

# Imports the top n rated movies on IMDB from OMDB
# Intended as a debug feature to quickly fill the database with some movies
# If this application would ever be used in the real world this would have to be ripped out
@login_required
@require_GET
def omdb_debug(request):
    n = request.GET.get('n')
    if n is None:
        amount = 10
    elif n.isdigit():
        amount = int(n)
    else:
        return json_bad_request()
    for id in top250[:amount]:
        omdb.import_from_omdb(id)
    return json_ok()

# Adds or removes a movie to a list
# Not a standalone view, used by the views for favorite and want to watch
def add_movie_to_list(request, movie_list, extra={}):
    id = request.POST.get('id')
    b = request.POST.get('b')
    if b not in ['0', '1'] or id is None:
        return json_bad_request()
    try:
        movie = Movie.objects.get(id=id)
    except Movie.DoesNotExist:
        return json_bad_request('Invalid ID')
    if b == '0':
        movie_list.remove(movie)
    else:
        movie_list.add(movie, **extra)        
    return json_ok()

# Favorites or unfavorites a movie
@login_required
@require_POST
def favorite(request):
    return add_movie_to_list(
        request, 
        request.user.profile.favorites)

# Adds or removes a movie from a user's want to watch list
@login_required
@require_POST
def want_to_watch(request):
    return add_movie_to_list(
        request, 
        request.user.profile.want_to_watch)

# Adds or removes a movie to a user's seen list
# Optional rating argument
@login_required
@require_POST
def seen(request):
    id = request.POST.get('id')
    b = request.POST.get('b')
    rating = request.POST.get('rating')
    # checking if all arguments are valid
    if b not in ['0', '1'] or id is None:
        return json_bad_request()
    # rating can be either None or a number between 0 and 10
    if rating is not None:
        if rating.isdigit():
            try:
                validate_score(int(rating))
            except:
                return json_bad_request()
        else:
            return json_bad_request()
    movie = Movie.objects.get(id=id)
    user = request.user.profile
    if movie is None:
        return json_bad_request('Invalid ID')
    
    if b == '0':
        MovieRating.objects.filter(movie=movie, user=user).delete()
        return json_ok()
    else:
        MovieRating.objects.update_or_create(
            user=user,
            movie=movie,
            defaults={'rating': rating},
        )
        return json_ok()

# This view should be seen as declaring the users intent to
# either be friends or no longer be friends with the specified user.
# Depending on the situation, a friend request is sent or withdrawn,
# the user added or removed from the friend list.
@login_required
@require_POST
def friend(request):
    id = request.POST.get('id')
    b = request.POST.get('b')
    if b not in ['0', '1'] or id is None:
        return json_bad_request()
    sender = request.user.profile
    try:
        receiver = User.objects.get(pk=id).profile
    except User.DoesNotExist:
        return json_404('No such user')
    out_req = FriendRequest.objects.filter(sender=sender, receiver=receiver).first()
    in_req = FriendRequest.objects.filter(sender=receiver, receiver=sender).first()
    if sender == receiver:
        return json_bad_request('You can\'t befriend yourself.')
    if b == '0':
        if out_req:
            # withdraw friend request
            out_req.delete()
        elif in_req:
            # delete other user's friend request
            in_req.delete()
        else:
            # remove user from friend list
            sender.friends.remove(receiver)
        return json_ok({
            'friendship_status': 'not_friends',
        })
    else:
        if in_req:
            # user's friend request deleted
            # users are now actual friends
            in_req.delete()
            sender.friends.add(receiver)
            return json_ok({
                'friendship_status': 'friends',
            })
        else:
            # friend request sent
            FriendRequest.objects.update_or_create(sender=sender, receiver=receiver)
            return json_ok({
                'friendship_status': 'pending',
            })

# Shows info for a movie
# Requires id of movie
@require_GET
def get_movie(request):
    id = request.GET.get('id')
    if id is None or not id.isdigit():
        return json_bad_request()

    try:
        movie = Movie.objects.get(pk=id)
    except Movie.DoesNotExist:
        return json_404()

    res = {
        'id': movie.pk,
        'title': movie.title,
        'description': movie.description,
        'year': movie.year,
        'runtime': f'{movie.runtime} min',
        'poster': movie.poster.url,
        'genres': ', '.join([str(g) for g in movie.genres.all()]),
        'url': movie.get_absolute_url()
    }
    return json_ok({'movie': res})
    