""" Copyright 2012, 2013 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.


This provides a management command to django's manage.py called create_consumer
that will generate a oauth key and secret based on the consumer name.

"""
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import hashlib
import time
import random
from oauth_provider.models import Consumer
from spotseeker_server.models import TrustedOAuthClient


class Command(BaseCommand):
    help = 'Creates a unique key and secret for clients connecting to the server'

    option_list = BaseCommand.option_list + (
        make_option('--name',
                    dest='consumer_name',
                    default=False,
                    help='A name for the consumer'),

        make_option('--trusted',
                    dest='trusted',
                    default=False,
                    help="Set to 'yes' if you want this client to be trusted to act for others")
    )

    def handle(self, *args, **options):
        if options['consumer_name']:
            consumer_name = options['consumer_name']
        else:
            consumer_name = raw_input('Enter consumer name: ')

        key = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()
        secret = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()

        consumer = Consumer.objects.create(name=consumer_name, key=key, secret=secret)

        if options['trusted'] and options['trusted'] == 'yes':
            trusted = TrustedOAuthClient.objects.create(consumer=consumer, is_trusted=1)

        self.stdout.write("Key: %s\n" % key)
        self.stdout.write("Secret: %s\n" % secret)
