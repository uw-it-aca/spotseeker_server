# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" This provides a management command to django's manage.py called
create_consumer that will generate a oauth key and secret based on the consumer
name.
"""
from optparse import make_option
import hashlib
import random
import string
import time

from django.core.management.base import BaseCommand, CommandError
from oauth_provider.models import Consumer

from spotseeker_server.models import TrustedOAuthClient


class Command(BaseCommand):
    help = (
        "Creates a unique key and secret for clients "
        "connecting to the server"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--name",
            dest="consumer_name",
            default=False,
            help="A name for the consumer",
        )

        parser.add_argument(
            "--trusted",
            dest="trusted",
            action="store_true",
            default=False,
            help="Makes this consumer trusted "
            "(Adds a TrustedOAuthClient for it)",
        )

        parser.add_argument(
            "--silent",
            dest="silent",
            action="store_true",
            default=False,
            help="With silent set, the command will generate no output",
        )

    def handle(self, *args, **options):
        if options["consumer_name"]:
            consumer_name = options["consumer_name"]
        else:
            consumer_name = input("Enter consumer name: ")

        key = hashlib.sha1(
            "{0} - {1}".format(random.random(), time.time()).encode("utf-8")
        ).hexdigest()

        # django-oauth-plus now wants secrets to be 16 chars
        secret = "".join(
            random.choice(string.ascii_letters + string.digits)
            for _ in range(16)
        )

        consumer = Consumer.objects.create(
            name=consumer_name, key=key, secret=secret
        )

        if options["trusted"]:
            trusted = TrustedOAuthClient.objects.create(
                consumer=consumer,
                is_trusted=1,
                bypasses_user_authorization=False,
            )

        if not options["silent"]:
            self.stdout.write("Key: %s\n" % key)
            self.stdout.write("Secret: %s\n" % secret)
