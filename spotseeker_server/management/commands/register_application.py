# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from io import StringIO
import contextlib

from django.core.management.base import BaseCommand, CommandParser

from spotseeker_server.models import Client

from oauth2_provider.management.commands import createapplication
from oauth2_provider.models import Application


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Register applications with Spotseeker."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '-s',
            '--show-credential',
            action='store_true',
            default=False,
            dest='show_credential',
            help="Print the credential created, very sensitive info.",
        )
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        if args and args[0]:
            name = args[0]
        else:
            name = input("Enter application name: ")

        logger.info("Registering application with Spotseeker...")

        # check if application already exists
        try:
            Application.objects.get(name=name)
            logger.info("Application already registered, skipping...")
            return
        except Application.DoesNotExist:
            pass

        output = StringIO()

        with contextlib.redirect_stdout(output):
            createapplication.Command().handle(
                name=name,
                client_type='confidential',
                authorization_grant_type='client-credentials',
                verbosity=0,
            )

        logger.debug("Getting client secret...")
        secret_len = 128
        end_char = output.tell()
        output.seek(end_char - secret_len - 1)
        client_secret = output.read(secret_len)
        output.close()

        logger.debug("Putting application into Client table...")

        app = Application.objects.get(name=name)
        Client.objects.create(
            username=name,
            name=name,
            client_id=app.client_id,
            client_secret=client_secret,
        )

        logger.debug("Compiling client credentials...")

        client = Client.objects.get(name=name)
        credential = client.get_client_credential()
        client.save()

        if options['show_credential']:
            logger.info("Credential: {}".format(credential))

        logger.info("Done.")
