#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/context_processors.py $
#   $Revision: 29352 $ $Date: 2012-04-23 15:45:00 -0500 (Mon, 23 Apr 2012) $

#   Copyright (c) 2010 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

"""
Provides request processors that return dictionaries to be merged into
the context for a template.  Each function takes the request object as
its only parameter and returns a dictionary to add to the context.

These are referenced using the setting TEMPLATE_CONTEXT_PROCESSORS
and are used by the RequestContext method.
"""

from django.core.exceptions import ValidationError

from sdg.django.auth import BluestemData

#####

def bluestem_auth(request):
    """
    Returns context data required by Django apps that use SDG's custom
    Bluestem authentication middleware.
    """

    bs_data = None

    try:
        bs_data = BluestemData(request.META)

    except ValidationError:
        pass

    return { 'bluestem' : bs_data }
