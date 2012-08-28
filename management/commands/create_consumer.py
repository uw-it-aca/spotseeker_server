"""
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
            dest='name',
            default=False,
            help='A name for the consumer'),

        make_option('--trusted',
            dest='trusted',
            default=False,
            help="Set to 'yes' if you want this client to be trusted to act for others"
        )

        )
    def handle(self, *args, **options):
        if options['name']:
            consumer_name = options['name']
        else:
            consumer_name = raw_input('Enter consumer name: ')

        key = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()
        secret = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()

        consumer = Consumer.objects.create(name=consumer_name, key=key, secret=secret)

        if options['trusted'] and options['trusted'] == 'yes':
            trusted = TrustedOAuthClient.objects.create(consumer=consumer, is_trusted=1)

        self.stdout.write("Key: %s\n" % key)
        self.stdout.write("Secret: %s\n" % secret)
