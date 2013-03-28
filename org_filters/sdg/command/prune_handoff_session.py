#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/command/prune_handoff_session.py $
#   $Revision: 33486 $ $Date: 2013-01-11 17:05:14 -0600 (Fri, 11 Jan 2013) $

#   Copyright (c) 2010 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''Prunes stale data from sdg.django.handoff.models AnnouncedSession.'''

import logging
import os
import sys

from optparse import OptionParser

import sdg

from sdg.log import StreamLog

def main(argv):
    '''Main function.'''

    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    StreamLog.init()

    #   Identify settings module and set environment appropriately
    sdg.set_settings_module()

    #   pylint: disable=F0401,E0611
    from sdg.django.handoff.models import AnnouncedSession
    
    opt_parser = OptionParser(argv)

    opt_parser.add_option('--days', dest='days', action='store', type='int',
                          help='number of days of data to be retained')

    (opt, leftover_arg_list) = opt_parser.parse_args()

    if len(leftover_arg_list):
        print opt_parser.get_usage()
        return 1

    try:
        if opt.days is not None:
            AnnouncedSession.prune(days=opt.days)
        else:
            AnnouncedSession.prune()

    #   pylint: disable=W0703
    except Exception, x:
        logging.info(x.message)
        return 1

    return 0

    #####

if __name__ == '__main__':
    sys.exit(main(sys.argv))
