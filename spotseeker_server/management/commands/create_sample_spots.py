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
    limitations under the License


    This provides a management command to django's manage.py called
    create_sample_spots that will generate a set of spots for testing.
"""
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from spotseeker_server.models import *
from django.contrib.auth.models import User
from django.core.files import File
from django.utils import timezone
from decimal import *
# from datetime import datetime
import os


class Command(BaseCommand):
    help = 'Deletes all existing spots, and creates new ones for testing.'

    option_list = BaseCommand.option_list + (
        make_option(
            '--force-delete',
            dest='delete_spots',
            default=False,
            help='Set to yes to force deletion of spots '
                 'without typing delete my spots',),
    )

    def handle(self, *args, **options):
        print ("This will delete all of your existing spots - if you "
               "really want to do that, type 'delete my spots':")

        if options['delete_spots'] == 'yes':
            confirmation = "delete my spots"
        else:
            confirmation = raw_input("Type it please: ")

        if confirmation != "delete my spots":
            raise CommandError("I'm only going to run if you're sure "
                               "you want to 'delete my spots'")
        else:
            Spot.objects.all().delete()
            SpotExtendedInfo.objects.all().delete()
            SpotAvailableHours.objects.all().delete()

            lab_space = Spot.objects.create(name="This is a computer lab",
                                            capacity=200,
                                            longitude=Decimal('-122.306644'),
                                            latitude=Decimal('47.658241'),
                                            building_name="Art Building")
            # get_or_create returns a tuple
            production_studio = \
                SpotType.objects.get_or_create(name="studio")[0]
            # get_or_create returns a tuple
            computer_lab = \
                SpotType.objects.get_or_create(name="computer_lab")[0]
            lab_space.spottypes.add(production_studio)
            lab_space.spottypes.add(computer_lab)
            lab_space.save()
            SpotExtendedInfo.objects.create(key="campus",
                                            value="seattle",
                                            spot=lab_space)

            # get_or_create returns a tuple
            cafe_type = SpotType.objects.get_or_create(name="cafe")[0]
            art = Spot.objects.create(name="In the Art Building - multiline "
                                           "name to test",
                                      capacity=10,
                                      longitude=Decimal('-122.306644'),
                                      latitude=Decimal('47.658241'),
                                      building_name="Art Building")
            art.spottypes.add(cafe_type)
            art.save()
            art_ada = SpotExtendedInfo.objects.create(key="location_"
                                                          "description",
                                                      value="This is the "
                                                            "location of the "
                                                            "space",
                                                            spot=art)
            art_ada = SpotExtendedInfo.objects.create(key='app_type',
                                                      value='food',
                                                      spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="has_whiteboards",
                                                      value="true",
                                                      spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="has_outlets",
                                                      value="true",
                                                      spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="has_displays",
                                                      value="true",
                                                      spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="has_printing",
                                                      value="true",
                                                      spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="has_scanner",
                                                      value="true",
                                                      spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="has_projector",
                                                      value="true",
                                                      spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="has_computers",
                                                      value="true",
                                                      spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="reservable",
                                                      value="true",
                                                      spot=art)
            art_ada = SpotExtendedInfo.objects.create(key="campus",
                                                      value="seattle",
                                                      spot=art)
            SpotExtendedInfo.objects.create(key="access_notes",
                                            value=" This space reservable "
                                                  "outside of TLC hours. To "
                                                  "reserve, go to http://www."
                                                  "tacoma.uw.edu/library/"
                                                  "reserve-group-study-rooms",
                                            spot=art)
            SpotExtendedInfo.objects.create(key="reservation_notes",
                                            value=" This space reservable "
                                                  "outside of TLC hours. To "
                                                  "reserve, go to http://www."
                                                  "tacoma.uw.edu/library/"
                                                  "reserve-group-study-rooms",
                                            spot=art)
            mgr = SpotExtendedInfo.objects.create(key="manager",
                                                  value="ctlt",
                                                  spot=art)
            org = SpotExtendedInfo.objects.create(key="organization",
                                                  value="Art",
                                                  spot=art)

            art2 = Spot.objects.create(name="Also in the Art Building",
                                       capacity=10,
                                       longitude=Decimal('-122.306644'),
                                       latitude=Decimal('47.658241'),
                                       building_name="Art Building")
            art2.spottypes.add(cafe_type)
            art2.save()
            art_ada = SpotExtendedInfo.objects.create(key="has_whiteboards",
                                                      value="true",
                                                      spot=art2)
            art_ada = SpotExtendedInfo.objects.create(key="has_outlets",
                                                      value="true",
                                                      spot=art2)
            art_ada = SpotExtendedInfo.objects.create(key="has_displays",
                                                      value="true",
                                                      spot=art2)
            art_ada = SpotExtendedInfo.objects.create(key="campus",
                                                      value="seattle",
                                                      spot=art2)
            mgr = SpotExtendedInfo.objects.create(key="manager",
                                                  value="ctlt",
                                                  spot=art2)
            org = SpotExtendedInfo.objects.create(key="organization",
                                                  value="Art",
                                                  spot=art2)

            base_dir = os.path.dirname(os.path.realpath(__file__))
            f = open(os.path.join(base_dir, 'resources', "building3.jpg"))
            art_img1 = SpotImage.objects.create(description="This is one "
                                                            "building",
                                                spot=art,
                                                image=File(f))
            f = open(os.path.join(base_dir, 'resources', "building4.jpg"))
            art_img2 = SpotImage.objects.create(description="This is another "
                                                            "building",
                                                spot=art,
                                                image=File(f))
            f = open(os.path.join(base_dir, 'resources', "building5.jpg"))
            art_img3 = SpotImage.objects.create(description="This is a third "
                                                            "art building",
                                                spot=art,
                                                image=File(f))

            f = open(os.path.join(base_dir, 'resources', "building6.jpg"))
            art_img4 = SpotImage.objects.create(description="This is a third "
                                                            "art building",
                                                spot=art,
                                                image=File(f))

            reviewer1, created = \
                User.objects.get_or_create(username='review1')
            reviewer2, created = \
                User.objects.get_or_create(username='review2')
            publisher1, created = \
                User.objects.get_or_create(username='publisher1')
            publisher2, created = \
                User.objects.get_or_create(username='publisher2')

            review1 = SpaceReview.objects.create(space=art,
                                                 reviewer=reviewer1,
                                                 published_by=publisher1,
                                                 review="Super duper space"
                                                        "\nReally nice.",
                                                 rating=5,
                                                 date_published=timezone.now(),
                                                 is_published=True)

            review2 = SpaceReview.objects.create(space=art,
                                                 reviewer=reviewer2,
                                                 published_by=publisher2,
                                                 review="OK space",
                                                 rating=4,
                                                 date_published=timezone.now(),
                                                 is_published=True)

            review3 = SpaceReview.objects.create(space=art,
                                                 reviewer=reviewer2,
                                                 published_by=publisher2,
                                                 review="Blah",
                                                 rating=1,
                                                 date_published=timezone.now(),
                                                 is_published=False)

            SpotExtendedInfo.objects.create(key="rating",
                                            value="4.5",
                                            spot=art)
            SpotExtendedInfo.objects.create(key="review_count",
                                            value="2",
                                            spot=art)

            study_room_type = \
                SpotType.objects.get_or_create(name="study_room")[0]
            tacoma = Spot.objects.create(name="WCG #1",
                                         capacity=20,
                                         longitude=Decimal('-122.437212'),
                                         latitude=Decimal('47.246213'),
                                         building_name="tacoma")
            tacoma.spottypes.add(study_room_type)
            tacoma.save()
            wcg_outlets = SpotExtendedInfo.objects.create(key="has_outlets",
                                                          value="true",
                                                          spot=tacoma)
            tacoma_outlets = SpotExtendedInfo.objects.create(key="campus",
                                                             value="tacoma",
                                                             spot=tacoma)
            mgr = SpotExtendedInfo.objects.create(key="manager",
                                                  value="ctlt",
                                                  spot=tacoma)
            org = SpotExtendedInfo.objects.create(key="organization",
                                                  value="Philosophy",
                                                  spot=tacoma)

            tacoma2 = Spot.objects.create(name="In tacoma - #2",
                                          capacity=20,
                                          longitude=Decimal('-122.437708'),
                                          latitude=Decimal('47.244832'),
                                          building_name="tacoma")
            tacoma2.spottypes.add(study_room_type)
            tacoma2.save()
            tacoma_outlets = SpotExtendedInfo.objects.create(key="has_outlets",
                                                             value="true",
                                                             spot=tacoma2)
            mgr = SpotExtendedInfo.objects.create(key="manager",
                                                  value="ctlt",
                                                  spot=tacoma2)
            mgr = SpotExtendedInfo.objects.create(key="campus",
                                                  value="tacoma",
                                                  spot=tacoma2)
            org = SpotExtendedInfo.objects.create(key="organization",
                                                  value="Economics",
                                                  spot=tacoma2)

            tacoma3 = Spot.objects.create(name="In tacoma - #2",
                                          capacity=20,
                                          longitude=Decimal('-122.438368'),
                                          latitude=Decimal('47.245838'),
                                          building_name="tacoma")
            tacoma3.spottypes.add(study_room_type)
            tacoma3.save()
            tacoma_outlets = SpotExtendedInfo.objects.create(key="has_outlets",
                                                             value="true",
                                                             spot=tacoma3)
            tacoma_outlets = SpotExtendedInfo.objects.create(key="campus",
                                                             value="tacoma",
                                                             spot=tacoma3)
            mgr = SpotExtendedInfo.objects.create(key="manager",
                                                  value="ctlt",
                                                  spot=tacoma3)
            org = SpotExtendedInfo.objects.create(key="organization",
                                                  value="Sociology",
                                                  spot=tacoma3)

            lounge_type = SpotType.objects.get_or_create(name="lounge")[0]
            fish_kitchen = \
                Spot.objects.create(name="FSH 2nd Floor South Kitchen",
                                    longitude=Decimal('-122.31659'),
                                    latitude=Decimal('47.65296'),
                                    building_name="Fishery Sciences",
                                    floor="2nd floor",
                                    room_number="266",
                                    capacity=12)
            fish_kitchen.spottypes.add(lounge_type)
            fish_kitchen.save()
            fish_outlets = SpotExtendedInfo.objects.create(key="has_outlets",
                                                           value="true",
                                                           spot=fish_kitchen)
            fish_outlets = SpotExtendedInfo.objects.create(key="campus",
                                                           value="seattle",
                                                           spot=fish_kitchen)
            mgr = SpotExtendedInfo.objects.create(key="manager",
                                                  value="ctlt",
                                                  spot=fish_kitchen)
            org = SpotExtendedInfo.objects.create(key="organization",
                                                  value="Fisheries",
                                                  spot=fish_kitchen)

            outdoor_type = SpotType.objects.get_or_create(name="outdoor")[0]
            fish_patio = Spot.objects.create(name="FSH 2nd Floor Patio/Deck",
                                             longitude=Decimal('-122.31659'),
                                             latitude=Decimal('47.65289'),
                                             building_name="Fishery Sciences",
                                             floor="2nd floor",
                                             capacity=12)
            fish_patio.spottypes.add(outdoor_type)
            fish_patio.save()
            fish_outlets = SpotExtendedInfo.objects.create(key="has_outlets",
                                                           value="true",
                                                           spot=fish_patio)
            fish_outlets = SpotExtendedInfo.objects.create(key="campus",
                                                           value="seattle",
                                                           spot=fish_patio)
            mgr = SpotExtendedInfo.objects.create(key="manager",
                                                  value="ctlt",
                                                  spot=fish_patio)
            org = SpotExtendedInfo.objects.create(key="organization",
                                                  value="Fisheries",
                                                  spot=fish_patio)

            for day in ["su", "m", "t", "w", "th", "f", "sa"]:
                SpotAvailableHours.objects.create(spot=lab_space,
                                                  day=day,
                                                  start_time="00:00",
                                                  end_time="23:59")
                SpotAvailableHours.objects.create(spot=art,
                                                  day=day,
                                                  start_time="00:00",
                                                  end_time="23:59")
                SpotAvailableHours.objects.create(spot=art2,
                                                  day=day,
                                                  start_time="00:00",
                                                  end_time="23:59")
                SpotAvailableHours.objects.create(spot=tacoma,
                                                  day=day,
                                                  start_time="00:00",
                                                  end_time="23:59")
                SpotAvailableHours.objects.create(spot=tacoma2,
                                                  day=day,
                                                  start_time="00:00",
                                                  end_time="23:59")
                SpotAvailableHours.objects.create(spot=tacoma3,
                                                  day=day,
                                                  start_time="00:00",
                                                  end_time="23:59")
                SpotAvailableHours.objects.create(spot=fish_kitchen,
                                                  day=day,
                                                  start_time="00:00",
                                                  end_time="23:59")
                SpotAvailableHours.objects.create(spot=fish_patio,
                                                  day=day,
                                                  start_time="00:00",
                                                  end_time="23:59")

            # Create rooms for Selenium testing
            # AA Balcony - like EE Patio but with different name/building
            aa_balcony = Spot.objects.create(name='AA Balcony',
                                             longitude=Decimal('-122.306371'),
                                             latitude=Decimal('47.653474'),
                                             building_name="Art Atrium")
            aa_balcony.spottypes.add(outdoor_type)
            aa_balcony.save()

            for day in ["su", "m", "t", "w", "th", "f", "sa"]:
                SpotAvailableHours.objects.create(spot=aa_balcony,
                                                  day=day,
                                                  start_time="00:00",
                                                  end_time="23:59")

            SpotExtendedInfo.objects.create(key="has_natural_light",
                                            value="true",
                                            spot=aa_balcony)
            SpotExtendedInfo.objects.create(key="food_nearby",
                                            value="neighboring",
                                            spot=aa_balcony)
            SpotExtendedInfo.objects.create(key="campus",
                                            value="seattle",
                                            spot=aa_balcony)
            SpotExtendedInfo.objects.create(key="location_description",
                                            value="Art Building Atrium",
                                            spot=aa_balcony)

            # Study Room 233 - like Study Room 332 but
            # with different name/building
            study_room_233 = Spot.objects.create(
                name='Study Room 233',
                capacity=8,
                longitude=Decimal('-122.306382'),
                latitude=Decimal('47.653477'),
                building_name="Library"
            )
            study_room_233.spottypes.add(study_room_type)
            study_room_233.save()

            SpotAvailableHours.objects.create(spot=study_room_233,
                                              day="f",
                                              start_time="00:00",
                                              end_time="20:00")
            SpotAvailableHours.objects.create(spot=study_room_233,
                                              day="sa",
                                              start_time="12:00",
                                              end_time="20:00")
            SpotAvailableHours.objects.create(spot=study_room_233,
                                              day="su",
                                              start_time="12:00",
                                              end_time="23:59")
            for day in ["m", "t", "w", "th"]:
                SpotAvailableHours.objects.create(spot=study_room_233,
                                                  day=day,
                                                  start_time="00:00",
                                                  end_time="23:59")

            SpotExtendedInfo.objects.create(key="location_description",
                                            value="Library, 2nd floor",
                                            spot=study_room_233)
            SpotExtendedInfo.objects.create(key="has_outlets",
                                            value="true",
                                            spot=study_room_233)
            SpotExtendedInfo.objects.create(key="has_printing",
                                            value="true",
                                            spot=study_room_233)
            SpotExtendedInfo.objects.create(key="has_whiteboards",
                                            value="true",
                                            spot=study_room_233)
            SpotExtendedInfo.objects.create(key="food_nearby",
                                            value="building",
                                            spot=study_room_233)
            SpotExtendedInfo.objects.create(key="reservable",
                                            value="true",
                                            spot=study_room_233)
            SpotExtendedInfo.objects.create(key="campus",
                                            value="seattle",
                                            spot=study_room_233)

            # Room 301 - like Room 201 but with different name/building
            room_301 = Spot.objects.create(name='Room 301',
                                           capacity=10,
                                           longitude=Decimal('-122.437708'),
                                           latitude=Decimal('47.244832'),
                                           building_name="Sad")
            room_301.spottypes.add(study_room_type)
            room_301.save()

            for day in ["m", "t", "w", "th"]:
                SpotAvailableHours.objects.create(spot=room_301,
                                                  day=day,
                                                  start_time="07:00",
                                                  end_time="22:00")

            for day in ["f", "sa", "su"]:
                SpotAvailableHours.objects.create(spot=room_301,
                                                  day=day,
                                                  start_time="07:00",
                                                  end_time="17:00")

            SpotExtendedInfo.objects.create(key="location_description",
                                            value="Sad, 3rd floor",
                                            spot=room_301)
            SpotExtendedInfo.objects.create(key="has_outlets",
                                            value="true",
                                            spot=room_301)
            SpotExtendedInfo.objects.create(key="has_natural_light",
                                            value="true",
                                            spot=room_301)
            SpotExtendedInfo.objects.create(key="food_nearby",
                                            value="building",
                                            spot=room_301)
            SpotExtendedInfo.objects.create(key="campus",
                                            value="tacoma",
                                            spot=room_301)

            food = Spot.objects.create(name="This is a food spot",
                                       capacity=10,
                                       longitude=Decimal('-122.3101087'),
                                       latitude=Decimal('47.6549552'),
                                       building_name="Food Building")
            food.spottypes.add(cafe_type)
            food.save()
            food_info = SpotExtendedInfo.objects.create(key='app_type',
                                                        value='food',
                                                        spot=food)
            food_info = SpotExtendedInfo.objects.create(key='has_outlets',
                                                        value='true',
                                                        spot=food)

            # get_or_create returns a tuple
            item_place_type = \
                SpotType.objects.get_or_create(name="checkout")[0]
            loan_office = Spot.objects.create(name="Tech Loan Office")
            loan_office.spottypes.add(item_place_type)
            loan_office.save()
            SpotExtendedInfo.objects.create(key='app_type',
                                            value='tech',
                                            spot=loan_office)
            SpotExtendedInfo.objects.create(key='has_cte_techloan',
                                            value='true',
                                            spot=loan_office)
            SpotExtendedInfo.objects.create(key='cte_techloan_id',
                                            value='1',
                                            spot=loan_office)

            macbook = Item.objects.create(name="Apple Macbook Pro",
                                          spot=loan_office,
                                          item_category="Placeholder Category",
                                          item_subcategory="Laptop Computer")
            ItemExtendedInfo.objects.create(key='i_quantity',
                                            value='10',
                                            item=macbook)
            ItemExtendedInfo.objects.create(key='i_model',
                                            value='Macbook Pro',
                                            item=macbook)
            ItemExtendedInfo.objects.create(key='i_brand',
                                            value='Apple',
                                            item=macbook)
            ItemExtendedInfo.objects.create(key='i_check_out_period',
                                            value='7',
                                            item=macbook)

            latitude = \
                Item.objects.create(name="Dell Latitude E5440",
                                    spot=loan_office,
                                    item_category="Placeholder Category",
                                    item_subcategory="Laptop Computer")
            ItemExtendedInfo.objects.create(key='i_quantity',
                                            value='12',
                                            item=latitude)
            ItemExtendedInfo.objects.create(key='i_model',
                                            value='Latitude E5440',
                                            item=latitude)
            ItemExtendedInfo.objects.create(key='i_brand',
                                            value='Dell',
                                            item=latitude)
            ItemExtendedInfo.objects.create(key='i_check_out_period',
                                            value='14',
                                            item=latitude)

            passport = \
                Item.objects.create(name="Fender Passport P-150",
                                    spot=loan_office,
                                    item_category="Placeholder Category",
                                    item_subcategory="Portable Audio System")
            ItemExtendedInfo.objects.create(key='i_quantity',
                                            value='5',
                                            item=passport)
            ItemExtendedInfo.objects.create(key='i_model',
                                            value='Passport P-150',
                                            item=passport)
            ItemExtendedInfo.objects.create(key='i_brand',
                                            value='Fender',
                                            item=passport)
            ItemExtendedInfo.objects.create(key='i_check_out_period',
                                            value='7',
                                            item=passport)
