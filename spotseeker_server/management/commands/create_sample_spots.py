# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-
"""     This provides a management command to django's manage.py called
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
import glob


class Command(BaseCommand):
    help = "Deletes all existing spots, and creates new ones for testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force-delete",
            "-f",
            action="store_true",
            dest="delete_spots",
            default=False,
            help="Set to yes to force deletion of spots "
            "without typing delete my spots",
        )

    def handle(self, *args, **options):
        if options["delete_spots"]:
            print("Deleting all existing spots...")
            confirmation = "delete my spots"
        else:
            print(
                "This will delete all of your existing spots - if you "
                "really want to do that, type 'delete my spots':"
            )
            confirmation = input("Type it please: ")

        if confirmation != "delete my spots":
            raise CommandError(
                "I'm only going to run if you're sure "
                "you want to 'delete my spots'"
            )
        else:
            Spot.objects.all().delete()
            SpotExtendedInfo.objects.all().delete()
            SpotAvailableHours.objects.all().delete()

            # delete old default images
            base_dir = os.path.dirname(os.path.realpath(__file__))
            path = os.path.join(base_dir, "resources")
            imgs = glob.glob(path + "/building*_*.jpg")
            for img in imgs:
                try:
                    os.remove(img)
                except OSError:
                    print("Could not delete image: " + img)

            lab_space = Spot.objects.create(
                name="This is a computer lab",
                capacity=200,
                longitude=Decimal("-122.306644"),
                latitude=Decimal("47.658241"),
                building_name="Art Building (ART)",
            )
            # get_or_create returns a tuple
            production_studio = SpotType.objects.get_or_create(name="studio")[
                0
            ]
            # get_or_create returns a tuple
            computer_lab = SpotType.objects.get_or_create(name="computer_lab")[
                0
            ]
            lab_space.spottypes.add(production_studio)
            lab_space.spottypes.add(computer_lab)
            lab_space.save()
            SpotExtendedInfo.objects.create(
                key="campus", value="seattle", spot=lab_space
            )

            # get_or_create returns a tuple
            cafe_type = SpotType.objects.get_or_create(name="cafe")[0]
            art = Spot.objects.create(
                name="In the Art Building - multiline " "name to test",
                capacity=10,
                longitude=Decimal("-122.306644"),
                latitude=Decimal("47.658241"),
                building_name="Art Building (ART)",
            )
            art.spottypes.add(cafe_type)
            art.save()
            art_ada = SpotExtendedInfo.objects.create(
                key="location_" "description",
                value="This is the " "location of the " "space",
                spot=art,
            )
            art_ada = SpotExtendedInfo.objects.create(
                key="app_type", value="food", spot=art
            )
            art_ada = SpotExtendedInfo.objects.create(
                key="has_whiteboards", value="true", spot=art
            )
            art_ada = SpotExtendedInfo.objects.create(
                key="has_outlets", value="true", spot=art
            )
            art_ada = SpotExtendedInfo.objects.create(
                key="has_displays", value="true", spot=art
            )
            art_ada = SpotExtendedInfo.objects.create(
                key="has_printing", value="true", spot=art
            )
            art_ada = SpotExtendedInfo.objects.create(
                key="has_scanner", value="true", spot=art
            )
            art_ada = SpotExtendedInfo.objects.create(
                key="has_projector", value="true", spot=art
            )
            art_ada = SpotExtendedInfo.objects.create(
                key="has_computers", value="true", spot=art
            )
            art_ada = SpotExtendedInfo.objects.create(
                key="reservable", value="true", spot=art
            )
            art_ada = SpotExtendedInfo.objects.create(
                key="campus", value="seattle", spot=art
            )
            SpotExtendedInfo.objects.create(
                key="access_notes",
                value=" This space reservable "
                "outside of TLC hours. To "
                "reserve, go to http://www."
                "tacoma.uw.edu/library/"
                "reserve-group-study-rooms",
                spot=art,
            )
            SpotExtendedInfo.objects.create(
                key="reservation_notes",
                value=" This space reservable "
                "outside of TLC hours. To "
                "reserve, go to http://www."
                "tacoma.uw.edu/library/"
                "reserve-group-study-rooms",
                spot=art,
            )
            mgr = SpotExtendedInfo.objects.create(
                key="manager", value="ctlt", spot=art
            )
            org = SpotExtendedInfo.objects.create(
                key="organization", value="Art", spot=art
            )

            art2 = Spot.objects.create(
                name="Also in the Art Building",
                capacity=10,
                longitude=Decimal("-122.306644"),
                latitude=Decimal("47.658241"),
                building_name="Art Building (ART)",
            )
            art2.spottypes.add(cafe_type)
            art2.save()
            art_ada = SpotExtendedInfo.objects.create(
                key="has_whiteboards", value="true", spot=art2
            )
            art_ada = SpotExtendedInfo.objects.create(
                key="has_outlets", value="true", spot=art2
            )
            art_ada = SpotExtendedInfo.objects.create(
                key="has_displays", value="true", spot=art2
            )
            art_ada = SpotExtendedInfo.objects.create(
                key="campus", value="seattle", spot=art2
            )
            mgr = SpotExtendedInfo.objects.create(
                key="manager", value="ctlt", spot=art2
            )
            org = SpotExtendedInfo.objects.create(
                key="organization", value="Art", spot=art2
            )

            base_dir = os.path.dirname(os.path.realpath(__file__))
            f = open(
                os.path.join(base_dir, "resources", "building3.jpg"), "rb"
            )
            art_img1 = SpotImage.objects.create(
                description="This is one " "building",
                spot=art,
                display_index=0,
                image=File(f),
            )
            f = open(
                os.path.join(base_dir, "resources", "building4.jpg"), "rb"
            )
            art_img2 = SpotImage.objects.create(
                description="This is another " "building",
                spot=art,
                display_index=1,
                image=File(f),
            )
            f = open(
                os.path.join(base_dir, "resources", "building5.jpg"), "rb"
            )
            art_img3 = SpotImage.objects.create(
                description="This is a third " "art building",
                spot=art,
                display_index=2,
                image=File(f),
            )

            f = open(
                os.path.join(base_dir, "resources", "building6.jpg"), "rb"
            )
            art_img4 = SpotImage.objects.create(
                description="This is a third " "art building",
                spot=art,
                display_index=3,
                image=File(f),
            )

            study_room_type = SpotType.objects.get_or_create(
                name="study_room"
            )[0]
            tacoma = Spot.objects.create(
                name="WCG #1",
                capacity=20,
                longitude=Decimal("-122.437212"),
                latitude=Decimal("47.246213"),
                building_name="West Coast Grocery " "(WCG)",
            )
            tacoma.spottypes.add(study_room_type)
            tacoma.save()
            wcg_outlets = SpotExtendedInfo.objects.create(
                key="has_outlets", value="true", spot=tacoma
            )
            tacoma_outlets = SpotExtendedInfo.objects.create(
                key="campus", value="tacoma", spot=tacoma
            )
            mgr = SpotExtendedInfo.objects.create(
                key="manager", value="ctlt", spot=tacoma
            )
            org = SpotExtendedInfo.objects.create(
                key="organization", value="Philosophy", spot=tacoma
            )

            tacoma2 = Spot.objects.create(
                name="In tacoma - #2",
                capacity=20,
                longitude=Decimal("-122.437708"),
                latitude=Decimal("47.244832"),
                building_name="West Coast Grocery " "(WCG)",
            )
            tacoma2.spottypes.add(study_room_type)
            tacoma2.save()
            tacoma_outlets = SpotExtendedInfo.objects.create(
                key="has_outlets", value="true", spot=tacoma2
            )
            mgr = SpotExtendedInfo.objects.create(
                key="manager", value="ctlt", spot=tacoma2
            )
            mgr = SpotExtendedInfo.objects.create(
                key="campus", value="tacoma", spot=tacoma2
            )
            org = SpotExtendedInfo.objects.create(
                key="organization", value="Economics", spot=tacoma2
            )

            tacoma3 = Spot.objects.create(
                name="In tacoma - #2",
                capacity=20,
                longitude=Decimal("-122.438368"),
                latitude=Decimal("47.245838"),
                building_name="West Coast Grocery " "(WCG)",
            )
            tacoma3.spottypes.add(study_room_type)
            tacoma3.save()
            tacoma_outlets = SpotExtendedInfo.objects.create(
                key="has_outlets", value="true", spot=tacoma3
            )
            tacoma_outlets = SpotExtendedInfo.objects.create(
                key="campus", value="tacoma", spot=tacoma3
            )
            mgr = SpotExtendedInfo.objects.create(
                key="manager", value="ctlt", spot=tacoma3
            )
            org = SpotExtendedInfo.objects.create(
                key="organization", value="Sociology", spot=tacoma3
            )

            lounge_type = SpotType.objects.get_or_create(name="lounge")[0]
            fish_kitchen = Spot.objects.create(
                name="FSH 2nd Floor South Kitchen",
                longitude=Decimal("-122.31659"),
                latitude=Decimal("47.65296"),
                building_name="Fishery Sciences (FSH)",
                floor="2nd floor",
                room_number="266",
                capacity=12,
            )
            fish_kitchen.spottypes.add(lounge_type)
            fish_kitchen.save()
            fish_outlets = SpotExtendedInfo.objects.create(
                key="has_outlets", value="true", spot=fish_kitchen
            )
            fish_outlets = SpotExtendedInfo.objects.create(
                key="campus", value="seattle", spot=fish_kitchen
            )
            mgr = SpotExtendedInfo.objects.create(
                key="manager", value="ctlt", spot=fish_kitchen
            )
            org = SpotExtendedInfo.objects.create(
                key="organization", value="Fisheries", spot=fish_kitchen
            )

            outdoor_type = SpotType.objects.get_or_create(name="outdoor")[0]
            fish_patio = Spot.objects.create(
                name="FSH 2nd Floor Patio/Deck",
                longitude=Decimal("-122.31659"),
                latitude=Decimal("47.65289"),
                building_name="Fishery Sciences " "(FSH)",
                floor="2nd floor",
                capacity=12,
            )
            fish_patio.spottypes.add(outdoor_type)
            fish_patio.save()
            fish_outlets = SpotExtendedInfo.objects.create(
                key="has_outlets", value="true", spot=fish_patio
            )
            fish_outlets = SpotExtendedInfo.objects.create(
                key="campus", value="seattle", spot=fish_patio
            )
            mgr = SpotExtendedInfo.objects.create(
                key="manager", value="ctlt", spot=fish_patio
            )
            org = SpotExtendedInfo.objects.create(
                key="organization", value="Fisheries", spot=fish_patio
            )

            for day in ["su", "m", "t", "w", "th", "f", "sa"]:
                SpotAvailableHours.objects.create(
                    spot=lab_space,
                    day=day,
                    start_time="00:00",
                    end_time="23:59",
                )
                SpotAvailableHours.objects.create(
                    spot=art, day=day, start_time="00:00", end_time="23:59"
                )
                SpotAvailableHours.objects.create(
                    spot=art2, day=day, start_time="00:00", end_time="23:59"
                )
                SpotAvailableHours.objects.create(
                    spot=tacoma, day=day, start_time="00:00", end_time="23:59"
                )
                SpotAvailableHours.objects.create(
                    spot=tacoma2, day=day, start_time="00:00", end_time="23:59"
                )
                SpotAvailableHours.objects.create(
                    spot=tacoma3, day=day, start_time="00:00", end_time="23:59"
                )
                SpotAvailableHours.objects.create(
                    spot=fish_kitchen,
                    day=day,
                    start_time="00:00",
                    end_time="23:59",
                )
                SpotAvailableHours.objects.create(
                    spot=fish_patio,
                    day=day,
                    start_time="00:00",
                    end_time="23:59",
                )

            # Create rooms for Selenium testing
            # AA Balcony - like EE Patio but with different name/building
            aa_balcony = Spot.objects.create(
                name="AA Balcony",
                longitude=Decimal("-122.306371"),
                latitude=Decimal("47.653474"),
                building_name="Art Atrium",
            )
            aa_balcony.spottypes.add(outdoor_type)
            f = open(
                os.path.join(base_dir, "resources", "building3.jpg"), "rb"
            )
            f2 = open(
                os.path.join(base_dir, "resources", "building4.jpg"), "rb"
            )
            aa_balcony_img = SpotImage.objects.create(
                description="This is one " "building",
                spot=aa_balcony,
                display_index=0,
                image=File(f),
            )
            aa_balcony_img2 = SpotImage.objects.create(
                description="This is one " "building",
                spot=aa_balcony,
                display_index=1,
                image=File(f2),
            )
            aa_balcony.save()

            for day in ["su", "m", "t", "w", "th", "f", "sa"]:
                SpotAvailableHours.objects.create(
                    spot=aa_balcony,
                    day=day,
                    start_time="00:00",
                    end_time="23:59",
                )

            SpotExtendedInfo.objects.create(
                key="has_natural_light", value="true", spot=aa_balcony
            )
            SpotExtendedInfo.objects.create(
                key="food_nearby", value="neighboring", spot=aa_balcony
            )
            SpotExtendedInfo.objects.create(
                key="campus", value="seattle", spot=aa_balcony
            )
            SpotExtendedInfo.objects.create(
                key="location_description",
                value="Art Building Atrium",
                spot=aa_balcony,
            )

            # Study Room 233 - like Study Room 332 but
            # with different name/building
            study_room_233 = Spot.objects.create(
                name="Study Room 233",
                capacity=8,
                longitude=Decimal("-122.306382"),
                latitude=Decimal("47.653477"),
                building_name="Odegaard Undergraduate Library (OUGL)",
            )
            study_room_233.spottypes.add(study_room_type)
            study_room_233.save()

            SpotAvailableHours.objects.create(
                spot=study_room_233,
                day="f",
                start_time="00:00",
                end_time="20:00",
            )
            SpotAvailableHours.objects.create(
                spot=study_room_233,
                day="sa",
                start_time="12:00",
                end_time="20:00",
            )
            SpotAvailableHours.objects.create(
                spot=study_room_233,
                day="su",
                start_time="12:00",
                end_time="23:59",
            )
            for day in ["m", "t", "w", "th"]:
                SpotAvailableHours.objects.create(
                    spot=study_room_233,
                    day=day,
                    start_time="00:00",
                    end_time="23:59",
                )

            SpotExtendedInfo.objects.create(
                key="location_description",
                value="Library, 2nd floor",
                spot=study_room_233,
            )
            SpotExtendedInfo.objects.create(
                key="has_outlets", value="true", spot=study_room_233
            )
            SpotExtendedInfo.objects.create(
                key="has_printing", value="true", spot=study_room_233
            )
            SpotExtendedInfo.objects.create(
                key="has_whiteboards", value="true", spot=study_room_233
            )
            SpotExtendedInfo.objects.create(
                key="food_nearby", value="building", spot=study_room_233
            )
            SpotExtendedInfo.objects.create(
                key="reservable", value="true", spot=study_room_233
            )
            SpotExtendedInfo.objects.create(
                key="campus", value="seattle", spot=study_room_233
            )

            # Room 301 - like Room 201 but with different name/building
            room_301 = Spot.objects.create(
                name="Room 301",
                capacity=10,
                longitude=Decimal("-122.437708"),
                latitude=Decimal("47.244832"),
                building_name="Joy",
            )
            room_301.spottypes.add(study_room_type)
            room_301.save()

            for day in ["m", "t", "w", "th"]:
                SpotAvailableHours.objects.create(
                    spot=room_301,
                    day=day,
                    start_time="07:00",
                    end_time="22:00",
                )

            for day in ["f", "sa", "su"]:
                SpotAvailableHours.objects.create(
                    spot=room_301,
                    day=day,
                    start_time="07:00",
                    end_time="17:00",
                )

            SpotExtendedInfo.objects.create(
                key="location_description",
                value="Sad, 3rd floor",
                spot=room_301,
            )
            SpotExtendedInfo.objects.create(
                key="has_outlets", value="true", spot=room_301
            )
            SpotExtendedInfo.objects.create(
                key="has_natural_light", value="true", spot=room_301
            )
            SpotExtendedInfo.objects.create(
                key="food_nearby", value="building", spot=room_301
            )
            SpotExtendedInfo.objects.create(
                key="campus", value="tacoma", spot=room_301
            )

            food = Spot.objects.create(
                name="This is a food spot",
                capacity=10,
                longitude=Decimal("-122.3101087"),
                latitude=Decimal("47.6549552"),
                building_name="Food Building",
            )
            food.spottypes.add(cafe_type)
            food.save()
            food_info = SpotExtendedInfo.objects.create(
                key="app_type", value="food", spot=food
            )
            food_info = SpotExtendedInfo.objects.create(
                key="has_outlets", value="true", spot=food
            )

            # get_or_create returns a tuple
            item_place_type = SpotType.objects.get_or_create(name="checkout")[
                0
            ]
            loan_office = Spot.objects.create(
                name="Tech Loan Office",
                building_name="Kane Hall (KNE)",
                longitude=Decimal("-122.306382"),
                latitude=Decimal("47.653477"),
            )
            loan_office.spottypes.add(item_place_type)
            loan_office.save()
            SpotExtendedInfo.objects.create(
                key="app_type", value="tech", spot=loan_office
            )
            SpotExtendedInfo.objects.create(
                key="has_cte_techloan", value="true", spot=loan_office
            )
            SpotExtendedInfo.objects.create(
                key="cte_techloan_id", value="1", spot=loan_office
            )
            SpotExtendedInfo.objects.create(
                key="campus", value="seattle", spot=loan_office
            )

            macbook = Item.objects.create(
                name="Apple Macbook Pro",
                spot=loan_office,
                item_category="Placeholder Category",
                item_subcategory="Laptop Computer",
            )
            f = open(
                os.path.join(base_dir, "resources", "building5.jpg"), "rb"
            )
            ItemImage.objects.create(
                item=macbook,
                image=File(f),
                display_index=0,
                description="Macbook Pro",
            )
            ItemExtendedInfo.objects.create(
                key="i_quantity", value="10", item=macbook
            )
            ItemExtendedInfo.objects.create(
                key="i_model", value="Macbook Pro", item=macbook
            )
            ItemExtendedInfo.objects.create(
                key="i_brand", value="Apple", item=macbook
            )
            ItemExtendedInfo.objects.create(
                key="i_check_out_period", value="7", item=macbook
            )
            ItemExtendedInfo.objects.create(
                key="i_is_active", value="true", item=macbook
            )

            latitude = Item.objects.create(
                name="Dell Latitude E5440",
                spot=loan_office,
                item_category="Placeholder Category",
                item_subcategory="Laptop Computer",
            )
            ItemExtendedInfo.objects.create(
                key="i_quantity", value="12", item=latitude
            )
            ItemExtendedInfo.objects.create(
                key="i_model", value="Latitude E5440", item=latitude
            )
            ItemExtendedInfo.objects.create(
                key="i_brand", value="Dell", item=latitude
            )
            ItemExtendedInfo.objects.create(
                key="i_check_out_period", value="14", item=latitude
            )
            ItemExtendedInfo.objects.create(
                key="i_is_active", value="true", item=latitude
            )

            passport = Item.objects.create(
                name="Fender Passport P-150",
                spot=loan_office,
                item_category="Placeholder Category",
                item_subcategory="Portable Audio System",
            )
            ItemExtendedInfo.objects.create(
                key="i_quantity", value="5", item=passport
            )
            ItemExtendedInfo.objects.create(
                key="i_model", value="Passport P-150", item=passport
            )
            ItemExtendedInfo.objects.create(
                key="i_brand", value="Fender", item=passport
            )
            ItemExtendedInfo.objects.create(
                key="i_check_out_period", value="7", item=passport
            )
            ItemExtendedInfo.objects.create(
                key="i_is_active", value="true", item=passport
            )

            other_office = Spot.objects.create(
                name="Another Loan Office",
                building_name="Kane Hall (KNE)",
                longitude=Decimal("-122.306382"),
                latitude=Decimal("47.653477"),
            )
            loan_office.spottypes.add(item_place_type)
            loan_office.save()
            SpotExtendedInfo.objects.create(
                key="app_type", value="tech", spot=other_office
            )
            SpotExtendedInfo.objects.create(
                key="has_cte_techloan", value="true", spot=other_office
            )
            SpotExtendedInfo.objects.create(
                key="cte_techloan_id", value="2", spot=other_office
            )
            SpotExtendedInfo.objects.create(
                key="campus", value="seattle", spot=other_office
            )

            thingy = Item.objects.create(
                name="Thingy P-150",
                spot=other_office,
                item_category="Placeholder Category",
                item_subcategory="Portable Audio System",
            )
            ItemExtendedInfo.objects.create(
                key="i_quantity", value="5", item=thingy
            )
            ItemExtendedInfo.objects.create(
                key="i_model", value="Passport P-150", item=thingy
            )
            ItemExtendedInfo.objects.create(
                key="i_brand", value="Fender", item=thingy
            )
            ItemExtendedInfo.objects.create(
                key="i_check_out_period", value="7", item=thingy
            )
            ItemExtendedInfo.objects.create(
                key="i_is_active", value="true", item=thingy
            )
