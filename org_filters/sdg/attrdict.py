#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/attrdict.py $
#   $Revision: 33486 $ $Date: 2013-01-11 17:05:14 -0600 (Fri, 11 Jan 2013) $

#   Copyright (c) 2012 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''Attribute dictionary module.'''

#####

class AttrDict(dict):
    '''Dictionary whose members can be accessed as attributes.'''

    #####

    def __init__(self, *args, **kwargs):
        '''New AttrDict object, inherited from dict.'''
        super(self.__class__, self).__init__(*args, **kwargs)
        return

    #####

    def __getattr__(self, name):
        '''Allows attribute reference to return dictionary member.'''
        return self.get(name)
