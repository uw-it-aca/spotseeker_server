# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" This provides a management command to django's manage.py called
create_consumer that will generate a client with a valid credential based on
the consumer name.
"""
import hashlib
import random
import string
import time

from django.core.management.base import BaseCommand

from spotseeker_server.models import TrustedOAuthClient, Client


class Command(BaseCommand):
    help = (
        "Creates a unique key and secret for clients "
        "connecting to the server"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "-n",
            "--name",
            dest="consumer_name",
            default=False,
            help="A name for the consumer",
        )

        parser.add_argument(
            "-t",
            "--trusted",
            dest="trusted",
            action="store_true",
            default=False,
            help="Makes this consumer trusted "
            "(Adds a TrustedOAuthClient for it)",
        )

        parser.add_argument(
            "-s",
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
            consumer_name = input("Enter client name: ")

        # key and secret can be anything, but we'll try to keep it unique
        key = hashlib.sha1(
            "{0} - {1}".format(random.random(), time.time()).encode("utf-8")
        ).hexdigest()

        secret = "".join(
            random.choice(string.ascii_letters + string.digits)
            for _ in range(16)
        )

        client = Client.objects.create(
            username=consumer_name,
            name=consumer_name, client_id=key, client_secret=secret
        )
        credential = client.get_client_credential()

        if options["trusted"]:
            trusted = TrustedOAuthClient.objects.create(
                consumer=client,
                is_trusted=True,
                bypasses_user_authorization=False,
            )

        if not options["silent"]:
            self.stdout.write(f"Credential: {credential}\n")
