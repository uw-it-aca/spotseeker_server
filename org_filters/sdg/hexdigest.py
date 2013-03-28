#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/hexdigest.py $
#   $Revision: 29352 $ $Date: 2012-04-23 15:45:00 -0500 (Mon, 23 Apr 2012) $

#   Copyright (c) 2010 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''
General-purpose randomization utilities for CITES Software Development Group
applications.
'''

from __future__ import absolute_import

import hashlib
import random
import re
import sys

from time import strftime

#   pylint: disable=E1101
HASH_CLASS          = hashlib.sha512    # Class of preferred hash algorithm
RANDOM_BITS         = 4096              # Number of random bits to use

#####

def generate_hexdigest():
    '''Generate a random number and return a hexadecimal digest.'''

    hclass = HASH_CLASS()
    hclass.update(str(random.Random().getrandbits(RANDOM_BITS)))

    return hclass.hexdigest()

#####

def read_hexdigest(path_random):
    '''
    Read a hexadecimal digest from specified file, ignoring comment
    lines and blank lines.
    '''

    #   Open specified file.
    digest_file = open(path_random, 'r')

    #   Iterate over lines in file.
    for line in digest_file:

        #   Strip newlines, comments, leading/trailing white space.
        line = line.rstrip("\n")

        line = re.sub("#.*", '', line)
        line = re.sub("^\s*", '', line)
        line = re.sub("\s*$", '', line)

        #   Do we have a usable token?
        if len(line) > 0:
            digest_file.close()

            if len(line) != 2 * HASH_CLASS().digest_size:
                raise ValueError \
                        ('digest has %d hexadecimal digits; expected %d' % 
                         (len(line), 2 * HASH_CLASS().digest_size))

            if re.search('[^a-fA-F0-9]', line):
                raise ValueError('digest contains non-hexadecimal characters')

            return line

    #   Reached end of file without finding usable token
    digest_file.close()
    raise ValueError('hexadecimal digest not found')

#####

def write_hexdigest(digest, path_random=None, description=None):
    '''
    Write a hexadecimal digest to standard output or to a file specified
    by path.
    '''
    if path_random:
        digest_file = open(path_random, 'w')

    else:
        digest_file = sys.stdout

    print >> digest_file, '#'
    print >> digest_file, '#\tservice secret (generated %s)' % \
                            strftime('%Y/%m/%d %H:%M:%S')

    if description:
        print >> digest_file, '#'
        print >> digest_file, '#\t%s' % description

    print >> digest_file, '#'
    print >> digest_file, digest
    return
