#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/auth/views.py $
#   $Revision: 29352 $ $Date: 2012-04-23 15:45:00 -0500 (Mon, 23 Apr 2012) $

#   Copyright (c) 2010 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''Package defines custom SDG logout view for Bluestem authentication.'''

import logging

from django.conf import settings
from django.contrib.auth.views import logout as builtin_logout_view

from sdg.django.auth import BluestemData
from sdg.django.auth import BLUESTEM_LOGOUT_PATH

#####

def bluestem_logout(request):
    '''
    Used in templates to provide a logout link that both logs a user 
    out of Django and Bluestem.
    
    Uses compiled-in BLUESTEM_LOGOUT_PATH default, which can be
    overridden by BLUESTEM_LOGOUT_PATH in settings file.
    '''

    #   Set the default BLUESTEM_LOGOUT_PATH for SMG-administered systems.
    logout_path = BLUESTEM_LOGOUT_PATH

    #   If settings file supplies the BLUESTEM_LOGOUT_PATH variable, use
    #   that path.

    if hasattr(settings, 'BLUESTEM_LOGOUT_PATH') and \
       settings.BLUESTEM_LOGOUT_PATH:
        logout_path = settings.BLUESTEM_LOGOUT_PATH

    bs_data = BluestemData(request.META)

    logging.info('logging out Bluestem ID \'%s\' as user \'%s\'',
                 bs_data, request.user)

    #   Invoke Django's builtin logout view and return response
    return builtin_logout_view(request, next_page=logout_path)
