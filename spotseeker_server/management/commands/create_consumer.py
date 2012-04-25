from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import hashlib
import time
import random
from oauth_provider.models import Consumer

class Command(BaseCommand):
    help = 'Creates a unique key and secret for clients connecting to the server'

    option_list = BaseCommand.option_list + (
        make_option('--name',
            dest='name',
            default=False,
            help='A name for the consumer'),
        )

    def handle(self, *args, **options):
        if options['name']:
            consumer_name = options['name']
        else:
            consumer_name = raw_input('Enter consumer name: ')

        key = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()
        secret = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()

        consumer = Consumer.objects.create(name=consumer_name, key=key, secret=secret)

        self.stdout.write("Key: %s\n" % key)
        self.stdout.write("Secret: %s\n" % secret)
