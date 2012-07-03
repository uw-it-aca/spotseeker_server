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

            cafe_type = SpotType.objects.get_or_create(name="cafe")[0]  # get_or_create returns a tuple
            art = Spot.objects.create(name="In the Art Building", capacity=10, longitude=Decimal('-122.306644'), latitude=Decimal('47.658241'), building_name="Art Building")
            art.spottypes.add(cafe_type)
            art.save()
            art_ada = SpotExtendedInfo.objects.create(key="has_whiteboards", value="true", spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="has_outlets", value="true", spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="has_displays", value="true", spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="has_printing", value="true", spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="has_scanner", value="true", spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="has_projector", value="true", spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="has_computers", value="true", spot=art)
            mgr = SpotExtendedInfo.objects.create(key="manager", value="ctlt", spot=art)
            org = SpotExtendedInfo.objects.create(key="organization", value="Art", spot=art)

            art2 = Spot.objects.create(name="Also in the Art Building", capacity=10, longitude=Decimal('-122.306644'), latitude=Decimal('47.658241'), building_name="Art Building")
            art2.spottypes.add(cafe_type)
            art2.save()
            art_ada = SpotExtendedInfo.objects.create(key="has_whiteboards", value="true", spot=art2)
            art_ada = SpotExtendedInfo.objects.create(key="has_outlets", value="true", spot=art2)
            art_ada = SpotExtendedInfo.objects.create(key="has_displays", value="true", spot=art2)
            mgr = SpotExtendedInfo.objects.create(key="manager", value="ctlt", spot=art2)
            org = SpotExtendedInfo.objects.create(key="organization", value="Art", spot=art2)

#            f = open("building1.jpg")
#            art_img1 = SpotImage.objects.create( description = "This is one building", spot=art, image = File(f) )
#            f = open("building2.jpg")
#            art_img2 = SpotImage.objects.create( description = "This is another building", spot=art, image = File(f) )
#            f = open("building3.jpg")
#            art_img3 = SpotImage.objects.create( description = "This is a third art building", spot=art, image = File(f) )

            study_room_type = SpotType.objects.get_or_create(name="study_room")[0]
            savery = Spot.objects.create(name="In Savery", capacity=20, longitude=Decimal('-122.308504'), latitude=Decimal('47.657041'), building_name="Savery")
            savery.spottypes.add(study_room_type)
            savery.save()
            savery_outlets = SpotExtendedInfo.objects.create(key="has_outlets", value="true", spot=savery)
            mgr = SpotExtendedInfo.objects.create(key="manager", value="ctlt", spot=savery)
            org = SpotExtendedInfo.objects.create(key="organization", value="Philosophy", spot=savery)

            savery2 = Spot.objects.create(name="In Savery - #2", capacity=20, longitude=Decimal('-122.308014'), latitude=Decimal('47.657041'), building_name="Savery")
            savery2.spottypes.add(study_room_type)
            savery2.save()
            savery_outlets = SpotExtendedInfo.objects.create(key="has_outlets", value="true", spot=savery2)
            mgr = SpotExtendedInfo.objects.create(key="manager", value="ctlt", spot=savery2)
            org = SpotExtendedInfo.objects.create(key="organization", value="Economics", spot=savery2)

            savery3 = Spot.objects.create(name="In Savery - #2", capacity=20, longitude=Decimal('-122.308014'), latitude=Decimal('47.657431'), building_name="Savery")
            savery3.spottypes.add(study_room_type)
            savery3.save()
            savery_outlets = SpotExtendedInfo.objects.create(key="has_outlets", value="true", spot=savery3)
            mgr = SpotExtendedInfo.objects.create(key="manager", value="ctlt", spot=savery3)
            org = SpotExtendedInfo.objects.create(key="organization", value="Sociology", spot=savery3)

            lounge_type = SpotType.objects.get_or_create(name="lounge")[0]
            fish_kitchen = Spot.objects.create(name="FSH 2nd Floor South Kitchen",
                                               longitude=Decimal('-122.31659'),
                                               latitude=Decimal('47.65296'),
                                               building_name="Fishery Sciences",
                                               floor="2nd floor",
                                               room_number="266",
                                               capacity=12)
            fish_kitchen.spottypes.add(lounge_type)
            fish_kitchen.save()
            fish_outlets = SpotExtendedInfo.objects.create(key="has_outlets", value="true", spot=fish_kitchen)
            mgr = SpotExtendedInfo.objects.create(key="manager", value="ctlt", spot=fish_kitchen)
            org = SpotExtendedInfo.objects.create(key="organization", value="Fisheries", spot=fish_kitchen)

            outdoor_type = SpotType.objects.get_or_create(name="outdoor")[0]
            fish_patio = Spot.objects.create(name="FSH 2nd Floor Patio/Deck",
                                               longitude=Decimal('-122.31659'),
                                               latitude=Decimal('47.65289'),
                                               building_name="Fishery Sciences",
                                               floor="2nd floor",
                                               capacity=12)
            fish_patio.spottypes.add(outdoor_type)
            fish_patio.save()
            fish_outlets = SpotExtendedInfo.objects.create(key="has_outlets", value="true", spot=fish_patio)
            mgr = SpotExtendedInfo.objects.create(key="manager", value="ctlt", spot=fish_patio)
            org = SpotExtendedInfo.objects.create(key="organization", value="Fisheries", spot=fish_patio)

            for day in ["su", "m", "t", "w", "th", "f", "sa"]:
                SpotAvailableHours.objects.create(spot=art, day=day, start_time="00:00", end_time="23:59")
                SpotAvailableHours.objects.create(spot=art2, day=day, start_time="00:00", end_time="23:59")
                SpotAvailableHours.objects.create(spot=savery, day=day, start_time="00:00", end_time="23:59")
                SpotAvailableHours.objects.create(spot=savery2, day=day, start_time="00:00", end_time="23:59")
                SpotAvailableHours.objects.create(spot=savery3, day=day, start_time="00:00", end_time="23:59")
                SpotAvailableHours.objects.create(spot=fish_kitchen, day=day, start_time="00:00", end_time="23:59")
                SpotAvailableHours.objects.create(spot=fish_patio, day=day, start_time="00:00", end_time="23:59")
