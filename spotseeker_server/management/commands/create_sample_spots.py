# -*- coding: utf-8 -*-
"""
This provides a management command to django's manage.py called create_sample_spots that will generate a set of spots for testing.
"""
from django.core.management.base import BaseCommand, CommandError
from spotseeker_server.models import *
from django.core.files import File
from decimal import *


class Command(BaseCommand):
    help = 'Deletes all existing spots, and creates new ones for testing.'

    def handle(self, *args, **options):
        print "This will delete all of your existing spots - if you really want to do that, type 'delete my spots':"

        confirmation = raw_input("Type it: ")

        if confirmation != "delete my spots":
            raise CommandError("I'm only going to run if you're sure you want to 'delete my spots'")
        else:
            Spot.objects.all().delete()
            SpotExtendedInfo.objects.all().delete()
            SpotAvailableHours.objects.all().delete()

            art = Spot.objects.create(name="In the Art Building", type_name="Café", capacity=10, longitude=Decimal('-122.306644'), latitude=Decimal('47.658241'))
            art_ada = SpotExtendedInfo.objects.create(key="ada_accessible", value="1", spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="has_whiteboards", value="1", spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="has_outlets", value="1", spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="has_monitors", value="1", spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="surfaces", value="Large, Flat", spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="seating", value="Comfy chairs", spot=art)

            art2 = Spot.objects.create(name="Also in the Art Building", type_name="Café", capacity=10, longitude=Decimal('-122.306644'), latitude=Decimal('47.658241'))
            art_ada = SpotExtendedInfo.objects.create(key="ada_accessible", value="1", spot=art2)
            art_ada = SpotExtendedInfo.objects.create(key="has_whiteboards", value="1", spot=art2)
            art_ada = SpotExtendedInfo.objects.create(key="has_outlets", value="1", spot=art2)
            art_ada = SpotExtendedInfo.objects.create(key="has_monitors", value="1", spot=art2)
            art_ada = SpotExtendedInfo.objects.create(key="surfaces", value="Large, Flat", spot=art2)
            art_ada = SpotExtendedInfo.objects.create(key="seating", value="Comfy chairs", spot=art2)

#            f = open("building1.jpg")
#            art_img1 = SpotImage.objects.create( description = "This is one building", spot=art, image = File(f) )
#            f = open("building2.jpg")
#            art_img2 = SpotImage.objects.create( description = "This is another building", spot=art, image = File(f) )
#            f = open("building3.jpg")
#            art_img3 = SpotImage.objects.create( description = "This is a third art building", spot=art, image = File(f) )

            savery = Spot.objects.create(name="In Savery", type_name="Study room", capacity=20, longitude=Decimal('-122.308504'), latitude=Decimal('47.657041'))
            savery_ada = SpotExtendedInfo.objects.create(key="ada_accessible", value="1", spot=savery)

            savery2 = Spot.objects.create(name="In Savery - #2", type_name="Study room", capacity=20, longitude=Decimal('-122.308014'), latitude=Decimal('47.657041'))
            savery_ada = SpotExtendedInfo.objects.create(key="ada_accessible", value="1", spot=savery2)

            savery3 = Spot.objects.create(name="In Savery - #2", type_name="Study room", capacity=20, longitude=Decimal('-122.308014'), latitude=Decimal('47.657431'))
            savery_ada = SpotExtendedInfo.objects.create(key="ada_accessible", value="1", spot=savery3)

            fish_kitchen = Spot.objects.create(name="FSH 2nd Floor South Kitchen",
                                               type_name="Lounge",
                                               longitude=Decimal('-122.31659'),
                                               latitude=Decimal('47.65296'),
                                               building_name="Fishery Sciences",
                                               floor="2nd floor",
                                               room_number="266",
                                               description="South wing",
                                               capacity=12)
            fish_ada = SpotExtendedInfo.objects.create(key="ada_accessible", value="1", spot=fish_kitchen)

            fish_patio = Spot.objects.create(name="FSH 2nd Floor Patio/Deck",
                                               type_name="Outdoor Area",
                                               longitude=Decimal('-122.31659'),
                                               latitude=Decimal('47.65289'),
                                               building_name="Fishery Sciences",
                                               floor="2nd floor",
                                               description="South wing",
                                               capacity=12)
            fish_ada = SpotExtendedInfo.objects.create(key="ada_accessible", value="1", spot=fish_patio)

            for day in ["su", "m", "t", "w", "th", "f", "sa"]:
                SpotAvailableHours.objects.create(spot=art, day=day, start_time="00:00", end_time="23:59")
                SpotAvailableHours.objects.create(spot=art2, day=day, start_time="00:00", end_time="23:59")
                SpotAvailableHours.objects.create(spot=savery, day=day, start_time="00:00", end_time="23:59")
                SpotAvailableHours.objects.create(spot=savery2, day=day, start_time="00:00", end_time="23:59")
                SpotAvailableHours.objects.create(spot=savery3, day=day, start_time="00:00", end_time="23:59")
                SpotAvailableHours.objects.create(spot=fish_kitchen, day=day, start_time="00:00", end_time="23:59")
                SpotAvailableHours.objects.create(spot=fish_patio, day=day, start_time="00:00", end_time="23:59")
