#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/management/commands/createsecretkey.py $
#   $Revision: 33486 $ $Date: 2013-01-11 17:05:14 -0600 (Fri, 11 Jan 2013) $

import os
import random
import sys

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

_DEFAULT_SECRET_KEY_FILENAME = 'secret_key'

class Command(BaseCommand):
    can_import_settings         = False
    help = ('Creates a Django project directory structure for the given '
            'project name in the current directory or optionally in the '
            'given directory.')
    requires_model_validation   = False

    _chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

    option_list = BaseCommand.option_list + \
        (
        make_option('--noinput', action='store_false', dest='interactive', 
                    default=True,
                    help='Tells Django to NOT prompt the user for input of any kind.'
                    ),

        make_option \
            ('--output-file', action='store', dest='output_file',
             default=_DEFAULT_SECRET_KEY_FILENAME, 
             help='Creates a Django secret key file which will be read '
                  'during the processing of a project\'s settings file.'
            ),
        )

    #####

    #   This method was stolen from Django.
    @staticmethod
    def get_random_string(length=12,
                          allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                        'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
        """
        Returns a securely generated random string.

        The default length of 12 with the a-z, A-Z, 0-9 character set returns
        a 71-bit value. log_2((26+26+10)^12) =~ 71 bits
        """
        return ''.join([random.choice(allowed_chars) for i in range(length)])

    #####

    def handle(self, *args, **options):
        interactive = options.get('interactive')
        output_path = options.get('output_file', _DEFAULT_SECRET_KEY_FILENAME)

        #   If output path exists and if we are interactive, prompt the
        #   user whether to overwrite the secret key file.
        if os.path.exists(output_path) and interactive:
            confirm = raw_input \
                ('''The secret key file already exists. Are you sure you want to overwrite it?

Type 'yes' to continue, or 'no' to cancel: '''
                    )

        else:                       
            #   Path doesn't exist or not interactive.
            confirm = 'yes'

        #   Interactive user didn't confirm
        if confirm != 'yes':
            print >> self.stderr, 'Creation of secret key cancelled.'
            return

        #   Open secret key file for writing.
        output_fp = open(output_path, 'w')

        #   Create a random value to use as SECRET_KEY hash to be used by
        #   the settings module, and write to secret key file.
        secret_key = self.get_random_string(50, self._chars)
        output_fp.write(secret_key)
        output_fp.close()

        print >> self.stderr, 'Secret key written to %s.' % \
            os.path.abspath(output_path)
        return
