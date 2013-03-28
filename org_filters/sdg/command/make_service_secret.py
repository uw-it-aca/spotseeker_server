#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/command/make_service_secret.py $
#   $Revision: 33486 $ $Date: 2013-01-11 17:05:14 -0600 (Fri, 11 Jan 2013) $

#   Copyright (c) 2010 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''Makes service secret for secure handoff of session between applications.'''

import os
import sys

from optparse import OptionParser

from sdg.hexdigest import generate_hexdigest, write_hexdigest

def main(argv):
    '''Main function.'''

    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    opt_parser = OptionParser()

    opt_parser.add_option('--description', dest='description', 
                          action='store',
                          help='description for service secret file')

    opt_parser.add_option('--output-file', dest='output_file_name',
                          action='store',
                          help='destination file for service secret')

    #   Explicit reference to argv is for benefit of unittest.
    opt, leftover_arg_list = opt_parser.parse_args(argv[1:])

    if len(leftover_arg_list):
        print >> sys.stderr, opt_parser.get_usage()
        sys.exit(1)

    write_hexdigest(generate_hexdigest(), 
                    path_random=opt.output_file_name, 
                    description=opt.description)

    sys.exit(0)

    #####

if __name__ == '__main__':
    sys.exit(main(sys.argv))
