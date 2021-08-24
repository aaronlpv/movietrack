from django.http import JsonResponse

# This file contains some functions for responding in JSON format
# Used by the API

bad_status = 'bad_request'
generic_error_msg = 'One or more required arguments are missing or invalid'

# Function to generate errors, generates generic "bad request" by default
def json_bad_request(error=generic_error_msg, status=bad_status, http_status=400):
    return JsonResponse({
        'status': status,
        'error': error
        }, status=http_status)

# Returns 404 message in json format
def json_404(error='Not found'):
    return json_bad_request(
        error=error,
        status="not_found",
        http_status=404
    )

def json_bad_method():
    return json_bad_request(
        error="Method Not Allowed",
        status="method_not_allowed",
        http_status=405
    )

# Function to return results if there were no errors
def json_ok(results = {}, safe=True):
    results['status'] = 'OK'
    return JsonResponse(results, safe=safe)

# Decorator for function-based views
# Checks if user is logged in and returns error if not
def login_required(func):
    def wrapper(request, **kwargs):
        if request.user.is_authenticated:
            return func(request, **kwargs)
        else:
            return json_bad_request(
                status="not_authenticated",
                error="Please log in to continue",
                http_status=401
            )
    return wrapper

# Decorator that only allows GET requests
def require_GET(func):
    def wrapper(request, **kwargs):
        if request.method == 'GET':
            return func(request, **kwargs)
        else:
            return json_bad_method()
    return wrapper

# Decorator that only allows POST requests
def require_POST(func):
    def wrapper(request, **kwargs):
        if request.method == 'POST':
            return func(request, **kwargs)
        else:
            return json_bad_method()
    return wrapper
