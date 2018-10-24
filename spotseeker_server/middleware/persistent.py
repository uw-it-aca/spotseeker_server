# from http://stackoverflow.com/questions/15896217/django-loading-a-page-that-
# has-external-authentication-changes-the-session-key


class PersistentSessionMiddleware(object):
    """ Injects the username into REMOTE_USER so that users continue to be
        logged in on views that don't require authentication.
    """
    def __init__(self):
        pass

    def process_request(self, request):
        header = "REMOTE_USER"

        if request.user.is_authenticated() and header not in request.META:
            request.META[header] = request.user.username
        return None
