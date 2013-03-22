# -*- coding: utf-8 -*-
""" Copyright 2012, 2013 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.


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
            art_ada = SpotExtendedInfo.objects.create(key="campus", value="seattle", spot=art)
            mgr = SpotExtendedInfo.objects.create(key="manager", value="ctlt", spot=art)
            org = SpotExtendedInfo.objects.create(key="organization", value="Art", spot=art)

            art2 = Spot.objects.create(name="Also in the Art Building", capacity=10, longitude=Decimal('-122.306644'), latitude=Decimal('47.658241'), building_name="Art Building")
            art2.spottypes.add(cafe_type)
            art2.save()
            art_ada = SpotExtendedInfo.objects.create(key="has_whiteboards", value="true", spot=art2)
            art_ada = SpotExtendedInfo.objects.create(key="has_outlets", value="true", spot=art2)
            art_ada = SpotExtendedInfo.objects.create(key="has_displays", value="true", spot=art2)
            art_ada = SpotExtendedInfo.objects.create(key="campus", value="seattle", spot=art2)
            mgr = SpotExtendedInfo.objects.create(key="manager", value="ctlt", spot=art2)
            org = SpotExtendedInfo.objects.create(key="organization", value="Art", spot=art2)

#            f = open("building1.jpg")
#            art_img1 = SpotImage.objects.create( description = "This is one building", spot=art, image = File(f) )
#            f = open("building2.jpg")
#            art_img2 = SpotImage.objects.create( description = "This is another building", spot=art, image = File(f) )
#            f = open("building3.jpg")
#            art_img3 = SpotImage.objects.create( description = "This is a third art building", spot=art, image = File(f) )

            study_room_type = SpotType.objects.get_or_create(name="study_room")[0]
            tacoma = Spot.objects.create(name="WCG #1", capacity=20, longitude=Decimal('-122.437212'), latitude=Decimal('47.246213'), building_name="tacoma")
            tacoma.spottypes.add(study_room_type)
            tacoma.save()
            wcg_outlets = SpotExtendedInfo.objects.create(key="has_outlets", value="true", spot=tacoma)
            tacoma_outlets = SpotExtendedInfo.objects.create(key="campus", value="tacoma", spot=tacoma)
            mgr = SpotExtendedInfo.objects.create(key="manager", value="ctlt", spot=tacoma)
            org = SpotExtendedInfo.objects.create(key="organization", value="Philosophy", spot=tacoma)

            tacoma2 = Spot.objects.create(name="In tacoma - #2", capacity=20, longitude=Decimal('-122.437708'), latitude=Decimal('47.244832'), building_name="tacoma")
            tacoma2.spottypes.add(study_room_type)
            tacoma2.save()
            tacoma_outlets = SpotExtendedInfo.objects.create(key="has_outlets", value="true", spot=tacoma2)
            mgr = SpotExtendedInfo.objects.create(key="manager", value="ctlt", spot=tacoma2)
            mgr = SpotExtendedInfo.objects.create(key="campus", value="tacoma", spot=tacoma2)
            org = SpotExtendedInfo.objects.create(key="organization", value="Economics", spot=tacoma2)

            tacoma3 = Spot.objects.create(name="In tacoma - #2", capacity=20, longitude=Decimal('-122.438368'), latitude=Decimal('47.245838'), building_name="tacoma")
            tacoma3.spottypes.add(study_room_type)
            tacoma3.save()
            tacoma_outlets = SpotExtendedInfo.objects.create(key="has_outlets", value="true", spot=tacoma3)
            tacoma_outlets = SpotExtendedInfo.objects.create(key="campus", value="tacoma", spot=tacoma3)
            mgr = SpotExtendedInfo.objects.create(key="manager", value="ctlt", spot=tacoma3)
            org = SpotExtendedInfo.objects.create(key="organization", value="Sociology", spot=tacoma3)

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
            fish_outlets = SpotExtendedInfo.objects.create(key="campus", value="seattle", spot=fish_kitchen)
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
            fish_outlets = SpotExtendedInfo.objects.create(key="campus", value="seattle", spot=fish_patio)
            mgr = SpotExtendedInfo.objects.create(key="manager", value="ctlt", spot=fish_patio)
            org = SpotExtendedInfo.objects.create(key="organization", value="Fisheries", spot=fish_patio)

            for day in ["su", "m", "t", "w", "th", "f", "sa"]:
                SpotAvailableHours.objects.create(spot=art, day=day, start_time="00:00", end_time="23:59")
                SpotAvailableHours.objects.create(spot=art2, day=day, start_time="00:00", end_time="23:59")
                SpotAvailableHours.objects.create(spot=tacoma, day=day, start_time="00:00", end_time="23:59")
                SpotAvailableHours.objects.create(spot=tacoma2, day=day, start_time="00:00", end_time="23:59")
                SpotAvailableHours.objects.create(spot=tacoma3, day=day, start_time="00:00", end_time="23:59")
                SpotAvailableHours.objects.create(spot=fish_kitchen, day=day, start_time="00:00", end_time="23:59")
                SpotAvailableHours.objects.create(spot=fish_patio, day=day, start_time="00:00", end_time="23:59")
