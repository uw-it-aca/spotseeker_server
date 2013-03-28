#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/__init__.py $
#   $Revision: 33515 $ $Date: 2013-01-15 17:59:04 -0600 (Tue, 15 Jan 2013) $

#   Copyright (c) 2010 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''
Package of SDG Django-related functions.
'''

#   Expose these methods to caller. (FIXME legacy)
from sdg.django.settings.custom import \
    CustomSettings, get_setting_names, get_setting_values

from sdg.django.settings._util import show_settings
