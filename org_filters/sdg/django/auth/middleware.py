#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/auth/middleware.py $
#   $Revision: 29352 $ $Date: 2012-04-23 15:45:00 -0500 (Mon, 23 Apr 2012) $

#   Copyright (c) 2010 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''Package of SDG custom authentication middleware for Django.'''

import logging

from django.conf import settings
from django.contrib import auth
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.urlresolvers import \
    (get_mod_func, RegexURLPattern, RegexURLResolver)
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.importlib import import_module

from sdg.django.auth import BluestemData

#####

class BluestemMiddleware(object):
    '''
    Middleware class for utilizing the Bluestem authentication
    backend in a Django application.

    If the request.user object is not already authenticated to Django, this
    middleware component uses the SDG Bluestem authentication backend, and
    attempts to authenticate the user via the BLUESTEM_ID_USER,
    BLUESTEM_ID_DOMAIN, and BLUESTEM_ID_AUTH environment variables provided
    in the Django HttpRequest object. If these variables are present (and
    sane), the user is automatically logged in to Django to persist the user
    in the Django session's request.user object.
    '''

    allow_anonymous_users   = False

    #####

    def _bluestem_authenticate(self, request):
        '''Perform Bluestem authentication on request object.'''

        #   If request.user attribute doesn't exist, AuthenticationMiddleware
        #   hasn't been loaded. Not much to do here but raise an exception.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured \
                (
                "The Django Bluestem auth middleware requires the"
                " authentication middleware to be installed. Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the BluestemMiddleware class. Also, you must set up"
                " the DATABASE_ settings in order to store the User model."
                )

        try:
            bs_data = BluestemData(request.META)

        except ValidationError:
            #   Raise runtime error if unable to construct BluestemData object
            raise RuntimeError \
                ('The web server does not appear to be correctly configured '
                 'for an application using the BluestemMiddleware '
                 'component. The required Bluestem environment variables '
                 'are not being passed to the application correctly.')
        
        # If the user is already authenticated and that user is the user we are
        # getting passed in the headers, then the correct user is already
        # persisted in the session and we don't need to continue.
        if request.user.is_authenticated():
            username = request.user.username
            if username == self.clean_username(bs_data.user, request):
                #   Already authenticated; return None to indicate success.
                return None             # already authenticated

            #   Handle mismatch by logging existing user out.
            auth.logout(request)
            logging.error \
                ('mismatch between \'%s\' and \'%s\'; user %s logged out',
                 username, bs_data.user, bs_data.user)

        # We are seeing this user for the first time in this session; attempt
        # to authenticate the user.
        user = auth.authenticate(bluestem_data=bs_data)

        if user:
            # User is valid. Set request.user and persist user in the session
            # by logging the user in.
            request.user = user
            auth.login(request, user)
            logging.info('accepting Bluestem ID \'%s\' as user \'%s\'',
                         bs_data, user)
            #   Authentication succeeded; return None to indicate success.
            return None

        #   Bluestem user was not found in local authorization database.
        #
        #   If allowing anonymous users, views MUST use methods like
        #   user.is_anonymous() and user.is_authenticated() to distinguish
        #   between anonymous and authenticated users.
        if not BluestemMiddleware.allow_anonymous_users:
            logging.error('Bluestem ID \'%s\' not known to application',                                  bs_data)
            return render_to_response('auth/not_authorized.html', 
                                      context_instance=RequestContext(request))

        #   Not authenticated, but return None to indicate success.
        return None

    #####

    def _init_excluded_views(self):
        '''
        Manage a cached object consisting of a set of object references to
        view functions that are excluded from Bluestem authentication.

        If the exclude set is available in Django's cache, it is returned
        to the caller.

        If the exclude set is not present in Django's cache, initialize
        exclude set as follows:

        *   Retrieve view names from the BLUESTEM_EXCLUDE setting.
        *   Load the module containing each view named in BLUESTEM_EXCLUDE
            to obtain the module's object reference.
        *   Add view object reference to the exclude set.
        *   Store exclude set into Django's cache.

        The cache timeout is determined from the timeout argument in the
        CACHE_BACKEND setting.
        '''

        #   Try to retrieve cached set of excluded views.
        excluded_view_set   = cache.get('excluded_view_set')
            
        #   Data is in cache; return excluded view set to caller.
        if excluded_view_set:
            return excluded_view_set
            
        #   Data is not present in cache; initialize empty set, and prepare
        #   to populate from settings.
        all_view_set            = CallbackSet()
        excluded_view_set       = CallbackSet()

        logging.debug('%s: caching excluded views', self.__class__.__name__)

        #   Import urlconf specified in settings file.
        urlconf = import_module(settings.ROOT_URLCONF)
        
        #   Create set to contain all view callbacks defined in urlconf.
        ##### TODO recursive.

        for url in urlconf.urlpatterns:
            #   If object is RegexURLResolver, iterate over all url_pattern
            #   values with callback attribute, and add callback function
            #   reference to all_view_set.
            if isinstance(url, RegexURLResolver):
                all_view_set.update \
                    (u.callback for u in url.url_patterns if u.callback)
                continue

            #   If object is RegexURLPattern, and has callback attribute,
            #   add callback function reference to all_view_set.
            if isinstance(url, RegexURLPattern) and url.callback:
                all_view_set.add(url.callback)

    #   logging.debug('found %d views:' % len(all_view_set))
    #   for callback in  all_view_set.sort():
    #       logging.debug('  %s' % all_view_set.format_callback(callback))

        #   Retrieve excluded views from settings file.
        try:
            exclude_list = settings.BLUESTEM_EXCLUDE

        except AttributeError:
            #   BLUESTEM_EXCLUDE attribute doesn't exist in settings, which
            #   implies that NO views are to be excluded. Store empty
            #   excluded views set into cache and return to caller.
            cache.set('excluded_view_set', excluded_view_set)
            return excluded_view_set

        #   Try looking up all views referenced in exclude list.
        for exclude_name in exclude_list:
            excluded_view_set.update(self._lookup_exclude(exclude_name))

        #   Store set of excluded views into cache and return to caller.
        cache.set('excluded_view_set', excluded_view_set)

    #   logging.debug('matched %d excluded views:' % len(excluded_view_set))
    #   for callback in  excluded_view_set.sort():
    #       logging.debug('  %s' % excluded_view_set.format_callback(callback))
        logging.debug('%d views excluded from Bluestem authentication: %s',
                      len(excluded_view_set), excluded_view_set)

        return excluded_view_set
    
    #####

    @classmethod
    def _lookup_exclude(cls, name):
        '''
        Used to process each object named in BLUESTEM_EXCLUDE setting.
        Attempts first to find as module ...
        '''

        #   Try importing name as module.
        try:
            mod = import_module(name)

        #   If name doesn't import as module, we go on to determine whether
        #   name is instead a view reference.
        except ImportError:
            pass

        #   Raise exception if something else is amiss with import.
        except ValueError:
            raise ImproperlyConfigured \
                    ('Error processing BLUESTEM_EXCLUDE. Is BLUESTEM_EXCLUDE '
                     'a correctly defined list or tuple?')

        #   Module import succeeded.
        else:
            #   If urlpatterns attribute isn't present; name isn't a proper
            #   url module reference.
            if not hasattr(mod, 'urlpatterns'):
                raise ImproperlyConfigured \
                        ('Module \'%s\' lacks a \'urlpatterns\' attribute' % \
                         mod.__name__)

            #   Return list of callback functions for every item in urlpatterns.
            return [ u.callback for u in mod.urlpatterns if u.callback ]

        #   Since name didn't import as module, we now see whether it's
        #   a reference to a view function contained in a module.
        mod_name, func_name = get_mod_func(name)

        #   Try importing containing module.
        try:
            mod = import_module(mod_name)
                
        #   Raise exception if module doesn't import.
        except ImportError:
            raise ImproperlyConfigured \
                    ('Name \'%s\' is neither url module or view' % name)

        #   Determine if named function is an attribute in module.
        try:
            view_func = getattr(mod, func_name)

        #   Not found; raise an exception.
        except AttributeError:
            raise ImproperlyConfigured \
                    ('Module \'%s\' does not define a \'%s\' view' % \
                     (mod_name, func_name))

        #   Return callback function for view. (Returned as list to be
        #   consistent with behavior when processing a name that's url module.)
        return [ view_func ]

    #####

    def clean_username(self, username, request):
        '''Invokes the backend's clean_username method if one is defined.'''

        #   Load backend.
        backend_key = request.session[auth.BACKEND_SESSION_KEY]
        backend     = auth.load_backend(backend_key)

        #   Invoke clean_username() method if present.
        try:
            username = backend.clean_username(username)

        #   Ignore exception from backend having no clean_username method.
        except AttributeError:      
            pass

        return username

    #####

    def process_view(self, request, callback, callback_args, callback_kwargs):
        '''
        Middleware component invoked during Django view processing to
        handle Bluestem authentication.
        '''

        #   Retrieve set containing excluded views.
        excluded_view_set = self._init_excluded_views()

        #   If view is excluded from Bluestem authentication, don't attempt
        #   to authenticate, and simply return None.
        if callback in excluded_view_set:
            logging.debug('%s.process_view: \'%s\' excluded',
                          self.__class__.__name__, 
                          CallbackSet.format_callback(callback))
            return None

        #   View is not excluded; perform Bluestem authentication and return
        #   result to caller.
        logging.debug('%s.process_view: \'%s\' included',
                     self.__class__.__name__, 
                     CallbackSet.format_callback(callback))
        return self._bluestem_authenticate(request)

class CallbackSet(set):
    '''Subclass of set() with a few extra methods and functions.'''

    def __str__(self):
        '''Return callbacks as sorted string.'''
        return ', '.join(self.format_callback(callback) 
                            for callback in self.sort())

    @staticmethod
    def format_callback(callback):
        '''Format callback as a Python object name.'''
        return '%s.%s' % (callback.__module__, callback.__name__)

    def sort(self):
        '''Sort callbacks in by module name and method name.'''
        return (callback for callback in sorted(self, key=self.format_callback))
