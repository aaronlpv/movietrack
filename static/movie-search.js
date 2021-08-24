/* Search suggestions */
/* Based on https://www.w3schools.com/xml/ajax_php.asp */
var suggestion_div = document.getElementById("search-suggestions")
function clearSuggestions() {
    suggestion_div.innerHTML = ""
}
function updateSuggestions(json_sug) {
    clearSuggestions()
    res = json_sug["results"]
    for(var i = 0, len = res.length; i < len; i++){
        /* Each suggestion is an <a> element containing
           the poster (<img>) and the title (<span>).
        */
        var link = document.createElement("a")
        link.setAttribute("href", res[i].url)
        link.setAttribute("class", "list-group-item suggestion")

        var poster = document.createElement("img")
        poster.setAttribute("src", res[i].poster)
        poster.setAttribute("class", "suggestion-poster")

        var title = document.createElement("span")
        title.setAttribute("class", "suggestion-title")
        title.innerText = res[i].title

        link.appendChild(poster)
        link.appendChild(title)
        suggestion_div.appendChild(link)
    }
}
function showSuggestions(title) {
    if(title.length == 0){
        clearSuggestions()
        return
    } else {
        $.ajax({
            url: "/api/movie-search/?q=" + title,
            dataType: "json"
        }).done(updateSuggestions)
    }
}

/* Movie detail list buttons
   These are all kind of the same
   They send a request to the server and when it succeeds,
   they update the page.
*/
function want_to_watch(){
    next = !movie.wtw
    $.ajax({
        url: "/api/want_to_watch/",
        data: {
            id: movie.id,
            b: (next ? "1" : "0"),
            csrfmiddlewaretoken: CSRF
        },
        dataType: "json",
        type: "POST"
    }).done(function(){
        if(next){
            $("#wtw-btn").attr("class", "btn btn-success mx-1")
        }else{
            $("#wtw-btn").attr("class", "btn btn-info mx-1")
        }
        movie.wtw = next
    })
}
function favorite(){
    next = !movie.favorited
    $.ajax({
        url: "/api/favorite/",
        data: {
            id: movie.id,
            b: (next ? "1" : "0"),
            csrfmiddlewaretoken: CSRF
        },
        dataType: "json",
        type: "POST"
    }).done(function(){
        if(next){
            $("#fav-btn").attr("class", "btn btn-success mx-1")
        }else{
            $("#fav-btn").attr("class", "btn btn-info mx-1")
        }
        movie.favorited = next
    })
}
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
/* 
When no score is passed to this function, it toggles whether a user has seen the movie that is being displayed.
If a score IS passed to this function, the movie is marked as seen and the score updated.
*/
function seen(score){
    // next is the next state for the 'seen' property
    // so true if a score is passed, else invert the previous state
    next = score !== undefined || !movie.seen
    data = {
        id: movie.id,
        b: (next ? "1" : "0"),
        csrfmiddlewaretoken: CSRF
    }
    if(score){
        data.rating = score
    }
    $.ajax({
        url: "/api/seen/",
        data: data,
        dataType: "json",
        type: "POST"
    }).done(function(){
        if(next){
            $("#seen-btn").attr("class", "btn btn-success mx-1")
        }else{
            $("#seen-btn").attr("class", "btn btn-info mx-1")
        }
        if(score){
            $("#user-rating").text(ratings[score])
            $("#rate-btn").attr("class", "btn btn-success mx-1")
        }else{
            $("#user-rating").text("Not rated")
            $("#rate-btn").attr("class", "btn btn-info mx-1")
        }
        movie.seen = next
    })
}
/* 
Kind of like the seen function,
it either toggles whether a user is a friend when b is not present,
or it updates depending on whether b is 1 or 0. 

To use this function a friends object should already be present in the global
JS environment.
*/
function friend(id, b){
    if(b !== undefined){
        next = b
    }else{
        next = !(id in friends)
    }
    $.post({
        url: "/api/friend/",
        data: {
            id: id,
            b: (next ? "1" : "0"),
            csrfmiddlewaretoken: CSRF
        },
        dataType: "json",
        type: "POST"
    }).done(function(resp){
        status = resp["friendship_status"]
        if(status == "friends"){
            friends[id] = true
            $("#friend-toggle-" + id).attr("class", "btn btn-success mx-1")
            $("#friend-status-" + id).text("Friends")
        }else if(status == "pending"){
            friends[id] = false
            $("#friend-toggle-" + id).attr("class", "btn btn-secondary mx-1")
            $("#friend-status-" + id).text("Friend request pending")
        }else{
            delete friends[id]
            $("#friend-toggle-" + id).attr("class", "btn btn-info mx-1")
            $("#friend-status-" + id).text("Add friend")
        }
    })
}
/* sidebar */
function hidesidebar() {
		// hide sidebar
        $('#sidebar').addClass('active');
        // hide overlay that hides movies
        $('.overlay').removeClass('active');
}
function getsidebar(){
	$("#sidebar").mCustomScrollbar({
         theme: "minimal"
    });
		// open sidebar
        $('#sidebar').removeClass('active');
		// fade in the overlay
		$('.overlay').addClass('active');
        // open/close dropdowns
        $('.collapse.in').toggleClass('in');
        // and also adjust aria-expanded attributes we use for the open/closed arrows
        // in our CSS
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');
}
		

