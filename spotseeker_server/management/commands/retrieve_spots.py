from django.core.management.base import BaseCommand, CommandError
from spotseeker_server.views.spot import SpotView
from optparse import make_option
from spotseeker_server.models import (Spot, SpotImage, FavoriteSpot,
                                      SpotAvailableHours, SpotExtendedInfo,
                                      SpaceReview, SharedSpace,
                                      SharedSpaceRecipient, Item, ItemImage,
                                      ItemExtendedInfo)
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.temp import NamedTemporaryFile
import base64
import oauth2
import json
import StringIO
from tempfile import SpooledTemporaryFile
import uuid
import time


class Command(BaseCommand):
    help = 'Retrieves spot JSON from a given search and then creates the spots\
            retrieved by that search within the current instance'

    option_list = BaseCommand.option_list + (
        make_option('--key',
                    dest='key',
                    default="",
                    help='The OAuth Key'),

        make_option('--secret',
                    dest='secret',
                    default="",
                    help="The Oauth secret"),

        make_option('--url',
                    dest='url',
                    default="",
                    help="The URL of the search/server to call"),

        make_option('--wipe',
                    dest='wipe',
                    action="store_true",
                    default="False",
                    help="Set this param if you'd like to wipe all spot data"),

        make_option('--no-images',
                    dest='no_images',
                    action="store_true",
                    default="False",
                    help="Set this param if you'd like to ignore images"),
    )

    def handle(self, *args, **options):
        if options["url"] == "":
            print "Please pass an URL!"
            return

        print ("This command should not be used as a production data " +
               "migration technique! It is only intended for development. Do" +
               " you wish to proceed? (Y/N)")

        response = raw_input()

        if not (response == "y" or response == "Y"):
            return
        consumer = oauth2.Consumer(key=options["key"],
                                   secret=options["secret"])

        client = oauth2.Client(consumer)
        url = options["url"]
        base_url = options["url"].split("api")[0][:-1]

        if options["wipe"]:
            print ("If you proceed here, all Spot/Space related data will be" +
                   " deleted! Do you wish to proceed? (Y/N)")

            response = raw_input()

            if not (response == "y" or response == "Y"):
                return
            Spot.objects.all().delete()
            SpotImage.objects.all().delete()
            FavoriteSpot.objects.all().delete()
            SpotAvailableHours.objects.all().delete()
            SpotExtendedInfo.objects.all().delete()
            Item.objects.all().delete()
            ItemImage.objects.all().delete()
            SpaceReview.objects.all().delete()
            SharedSpace.objects.all().delete()

        start_time = time.time()
        # make request to URLmodels.Model
        resp, content = client.request(url, method="GET")

        if resp.status != 200:
            print "Request failed with status code: " + str(resp.status)
            return

        # load spot JSON, create spots
        spot_json = json.loads(content)

        if not isinstance(spot_json, list):
            spot_json = [spot_json]

        class FakeRequest(object):

            def __init__(self, body):
                self.body = body

            def read(self):
                return self.body

        view = SpotView()
        json_to_model = {}

        for spot in spot_json:

            fake_req = FakeRequest(json.dumps(spot))
            try:
                # Create spot
                view.build_and_save_from_input(fake_req, None)
                spot_model = Spot.objects.latest('pk')
                content_types = {v: k for k, v in
                                 SpotImage.CONTENT_TYPES.iteritems()}

                if options["no_images"]:
                    continue

                # retrieve spot images
                for image in spot["images"]:
                    resp, content = client.request(base_url + image["url"],
                                                   method="GET")
                    im = SpotImage()
                    im.spot = spot_model
                    im.descrition = image["description"]
                    im.width = image["width"]
                    im.height = image["height"]
                    im.display_index = image["display_index"]
                    im.upload_application = "retrieve_spots_command"
                    im.upload_user = "n/a"
                    im.image.save(str(uuid.uuid4()) + "." +
                                  content_types[resp["content-type"]],
                                  SimpleUploadedFile(str(uuid.uuid4()) + "." +
                                  content_types[resp["content-type"]],
                                  content, resp["content-type"]))
                    im.save()
            except Exception as ex:
                print "Spot ID # " + str(spot["id"]) + " failed to save!"
                for field, errors in ex.form.errors.items():
                    print "{}: {}".format(ex.form.data, errors.as_text())

        end_time = time.time()
        print 'Function took %0.3f s' % (end_time - start_time)
