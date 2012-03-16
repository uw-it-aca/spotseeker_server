from django.http import HttpResponse
from spotseeker_server.require_auth import *

def search(request):
    if "GET" == request.META['REQUEST_METHOD']:
        @app_auth_required
        def run(request):
            return HttpResponse("This is the search resource")
        return run(request)
    else:
        return invalid_method(request)

def spot(request, spot_id):
    if "GET" == request.META['REQUEST_METHOD']:
        @app_auth_required
        def run(request, spot_id):
            return HttpResponse("This is the view for spot id: "+spot_id)
        return run(request, spot_id)
    elif "PUT" == request.META['REQUEST_METHOD']:
        @user_auth_required
        def run(request, spot_id):
            return HttpResponse("This should be a PUT for spot id: "+spot_id)
        return run(request, spot_id)
    elif "DELETE" == request.META['REQUEST_METHOD']:
        @user_auth_required
        def run(request, spot_id):
            return HttpResponse("This should be a DELETE for spot id: "+spot_id)
        return run(request, spot_id)
    else:
        return invalid_method(request)

def add_image(request, spot_id):
    if "POST" == request.META['REQUEST_METHOD']:
        @user_auth_required
        def run(request, spot_id):
            return HttpResponse("This should add a new image for: "+spot_id)
        return run(request, spot_id)
    else:
        return invalid_method(request)

def view_image(request, spot_id, image_id):
    if "GET" == request.META['REQUEST_METHOD']:
        @app_auth_required
        def run(request, spot_id, image_id):
            return HttpResponse("This should be image data.  spot id: "+spot_id+" image id: "+image_id)
        return run(request, spot_id, image_id)
    else:
        return invalid_method(request)

def view_thumbnail(request, spot_id, image_id, thumb_width, thumb_height):
    if "GET" == request.META['REQUEST_METHOD']:
        @app_auth_required
        def run(request, spot_id, image_id, thumb_width, thumb_height):
            return HttpResponse("This should be thumbnailed image data.  spot id: "+spot_id+" image id: "+image_id+ " width: "+thumb_width+" height: "+thumb_height)
        return run(request, spot_id, image_id, thumb_width, thumb_height)
    else:
        return invalid_method(request)


def invalid_method(request):
    response = HttpResponse("Method not allowed")
    response.status_code = 405

    return response


