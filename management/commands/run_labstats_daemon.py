"""
This provides a managament command to run a daemon that will frequently update
the spots that have corresponding labstats information with the number of
machines available and similar information.
"""
from spotseeker_server.models import Spot, SpotExtendedInfo
from django.core.management.base import BaseCommand
from django.conf import settings
from optparse import make_option
from datetime import datetime
from SOAPpy import WSDL
import os
import sys
import time
import atexit
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'This updates spots with labstats data'

    option_list = BaseCommand.option_list + (
        make_option('--daemonize',
                    dest='daemon',
                    default=True,
                    action='store_true',
                    help='This will set the updater to run as a daemon.'),
        make_option('--update-delay',
                    dest='update_delay',
                    type='float',
                    default=60,
                    help='The number of seconds between update attempts.'),
        make_option('--run-once',
                    dest='run_once',
                    default=False,
                    action='store_true',
                    help='This will allow the updater to run just once.'),
    )

    def handle(self, *args, **options):
        """
        This is the entry point for the management command. It will handle
        daemonizing the script as needed.
        """

        atexit.register(self.remove_pid_file)

        daemon = options["daemon"]

        if daemon:
            logger.debug("starting the updater as a daemon")
            pid = os.fork()
            if pid == 0:
                os.setsid()

                pid = os.fork()
                if pid != 0:
                    os._exit(0)

            else:
                os._exit(0)

            self.create_pid_file()
            try:
                self.controller(options["update_delay"], options["run_once"])
            except Exception as ex:
                logger.error("Error running the controller: %s", str(ex))

        else:
            logger.debug("starting the updater as an interactive process")
            self.create_pid_file()
            self.controller(options["update_delay"], options["run_once"])

    def controller(self, update_delay, run_once=False):
        """
        This is responsible for the workflow of orchestrating
        the updater process.
        """

        # Set the last queue retry time to now - don't want it to run in the
        # first round of the controller running
        last_dispatch_retry_time = datetime.now()
        last_job_retry_time = datetime.now()

        while True:
            if self.should_stop():
                sys.exit()

            # This allows for a one time run via interactive process for automated testing
            if run_once:
                self.create_stop_file()

            try:
                # Updates the num_machines_available extended_info field for spots that have corresponding labstats.
                stats = WSDL.Proxy(settings.LABSTATS_URL)
                groups = stats.GetGroupedCurrentStats().GroupStat

                # TODO: when UIUC's changes with the external_id have been merged in, update the following
                # to use the external_id field instead of the labstats_id extended_info field

                #labstats_spaces = Spot.objects.exclude(external_id="") < -- for after the UIUC changes
                labstats_spaces = Spot.objects.filter(spotextendedinfo__key="labstats_id")  # delete this after external_id is used

                for space in labstats_spaces:
                    try:
                        for g in groups:
                            # Available data fields froms the labstats groups:
                            # g.groupName g.availableCount g.groupId g.inUseCount g.offCount g.percentInUse g.totalCount g.unavailableCount

                            # if space.external_id == g.groupName: <-- for after the UIUC changes
                            if space.spotextendedinfo_set.get(key="labstats_id").value == g.groupName:  # delete this after external_id is used

                                if not SpotExtendedInfo.objects.filter(spot=space, key="__auto_labstats_total"):
                                    SpotExtendedInfo.objects.create(spot=space, key="__auto_labstats_available", value=g.availableCount)
                                    SpotExtendedInfo.objects.create(spot=space, key="__auto_labstats_total", value=g.totalCount)
                                    SpotExtendedInfo.objects.create(spot=space, key="__auto_labstats_off", value=g.offCount)

                                else:
                                    SpotExtendedInfo.objects.filter(spot=space, key="__auto_labstats_available").update(value=g.availableCount)
                                    SpotExtendedInfo.objects.filter(spot=space, key="__auto_labstats_total").update(value=g.totalCount)
                                    SpotExtendedInfo.objects.filter(spot=space, key="__auto_labstats_off").update(value=g.offCount)

                    except Exception as ex:
                        logger.debug("An error occured updating labstats spots: %s", str(ex))

            except Exception as ex:
                logger.debug("Error getting labstats stats: %s", str(ex))

            if not run_once:
                time.sleep(update_delay)
                if self.should_stop():
                    sys.exit()
            else:
                sys.exit()

    def read_pid_file(self):
        if os.path.isfile(self._get_pid_file_path()):
            return True
        return False

    def create_pid_file(self):
        handle = open(self._get_pid_file_path(), 'w')
        handle.write(str(os.getpid()))
        handle.close()
        return

    def create_stop_file(self):
        handle = open(self._get_stopfile_path(), 'w')
        handle.write(str(os.getpid()))
        handle.close()
        return

    def remove_pid_file(self):
        os.remove(self._get_pid_file_path())

        if os.path.isfile(self._get_stopfile_path()):
            self.remove_stop_file()

    def remove_stop_file(self):
        os.remove(self._get_stopfile_path())

    def _get_pid_file_path(self):
        if not os.path.isdir("/tmp/updater/"):
            os.mkdir("/tmp/updater/", 0700)
        return "/tmp/updater/%s.pid" % (str(os.getpid()))

    def should_stop(self):
        if os.path.isfile(self._get_stopfile_path()):
            self.remove_stop_file()
            return True
        return False

    def _get_stopfile_path(self):
        if not os.path.isdir("/tmp/updater/"):
            os.mkdir("/tmp/updater/", 0700)
        return "/tmp/updater/%s.stop" % (str(os.getpid()))
