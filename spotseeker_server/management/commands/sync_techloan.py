import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from schema import Schema

from .techloan.techloan import Techloan
from .techloan.spotseeker import Spots


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync techloan data from the cte"

    _settings_scheme = Schema({
        'server_host': str,
        'oauth_key': str,
        'oauth_secret': str,
        'oauth_user': str,
    })

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        try:
            self._settings_scheme.validate(
                settings.SPOTSEEKER_TECHLOAN_UPDATER)
        except Exception as ex:
            logger.error("Settings misconfigured: ", ex)
            return

        techloan = Techloan.from_cte_api()
        spots = Spots.from_spotseeker_server(
            settings.SPOTSEEKER_TECHLOAN_UPDATER)

        spots.sync_with_techloan(techloan)
        spots.upload_data()
