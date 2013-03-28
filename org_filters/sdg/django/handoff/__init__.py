#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/handoff/__init__.py $
#   $Revision: 33486 $ $Date: 2013-01-11 17:05:14 -0600 (Fri, 11 Jan 2013) $

#   Copyright (c) 2011 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''
Package of SDG functions related to handing off one web application to another
under Django.
'''

from _wsapi import WSAPI, WSAPIAnnouncer, WSAPIClient, WSAPIServer
