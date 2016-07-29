""" Copyright 2012-2014 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from django.utils import unittest

from spotseeker_server.test.buildings import BuildingTest
from spotseeker_server.test.models import SpotModelToStringTests
from spotseeker_server.test.models import SpotExtendedInfoTests
from spotseeker_server.test.spot_form import SpotFormTest
from spotseeker_server.test.spot_model import SpotModelTest
from spotseeker_server.test.spot_put import SpotPUTTest
from spotseeker_server.test.spot_delete import SpotDELETETest
from spotseeker_server.test.spot_post import SpotPOSTTest
from spotseeker_server.test.spot_get import SpotGETTest
from spotseeker_server.test.favorite_model import FavoriteSpotTest
from spotseeker_server.test.no_rest_methods import NoRESTMethodsTest
from spotseeker_server.test.schema import SpotSchemaTest
from spotseeker_server.test.images.get import SpotImageGETTest
from spotseeker_server.test.images.post import SpotImagePOSTTest
from spotseeker_server.test.images.put import SpotImagePUTTest
from spotseeker_server.test.images.delete import SpotImageDELETETest
from spotseeker_server.test.images.thumb import ImageThumbTest
from spotseeker_server.test.images.spot_info import SpotResourceImageTest
from spotseeker_server.test.images.oauth_spot_info import \
    SpotResourceOAuthImageTest
from spotseeker_server.test.search.buildings import BuildingSearchTest
from spotseeker_server.test.search.capacity import SpotSearchCapacityTest
from spotseeker_server.test.search.limit import SpotSearchLimitTest
from spotseeker_server.test.search.distance import SpotSearchDistanceTest
from spotseeker_server.test.search.fields import SpotSearchFieldTest
from spotseeker_server.test.search.distance_fields import \
    SpotSearchDistanceFieldTest
from spotseeker_server.test.search.view_methods import \
    SpotSearchViewMethodsTest
from spotseeker_server.test.search.time import SpotSearchTimeTest
from spotseeker_server.test.hours.model import SpotHoursModelTest
from spotseeker_server.test.hours.get import SpotHoursGETTest
from spotseeker_server.test.hours.put import SpotHoursPUTTest
from spotseeker_server.test.hours.post import SpotHoursPOSTTest
from spotseeker_server.test.hours.open_now import SpotHoursOpenNowTest
from spotseeker_server.test.hours.open_at import SpotHoursOpenAtTest
from spotseeker_server.test.hours.open_until import SpotHoursOpenUntilTest
from spotseeker_server.test.hours.hours_range import HoursRangeTest
from spotseeker_server.test.hours.open_now_location import \
    SpotHoursOpenNowLocationTest
from spotseeker_server.test.hours.open_now_location_attributes import \
    SpotHoursOpenNowLocationAttributesTest
from spotseeker_server.test.hours.overlap import SpotHoursOverlapTest
from spotseeker_server.test.hours.modify import SpotHoursModifyTest
from spotseeker_server.test.auth.all_ok import SpotAuthAllOK
from spotseeker_server.test.auth.oauth import SpotAuthOAuth
from spotseeker_server.test.auth.oauth_logger import SpotAuthOAuthLogger
from spotseeker_server.test.uw_spot.spot_form import UWSpotFormTest
from spotseeker_server.test.uw_spot.spot_post import UWSpotPOSTTest
from spotseeker_server.test.uw_spot.spot_put import UWSpotPUTTest
from spotseeker_server.test.uw_spot.schema import UWSpotSchemaTest
from spotseeker_server.test.uw_spot.uw_search import UWSearchTest
from spotseeker_server.test.favorites import FavoritesTest
from spotseeker_server.test.share_space import ShareSpaceTest
from spotseeker_server.test.reviews import ReviewsTest
from spotseeker_server.test.future.future_get import FutureGETTest
from spotseeker_server.test.future.future_put import FuturePUTTest
