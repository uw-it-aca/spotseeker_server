# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

# Use full test failure messages
import spotseeker_server.test.long_message

from spotseeker_server.test.buildings import BuildingTest
from spotseeker_server.test.models import SpotModelToStringTests
from spotseeker_server.test.spot_form import DefaultSpotFormTest
from spotseeker_server.test.spot_model import SpotModelTest
from spotseeker_server.test.spot_put import SpotPUTTest
from spotseeker_server.test.spot_delete import SpotDELETETest
from spotseeker_server.test.spot_post import SpotPOSTTest
from spotseeker_server.test.spot_get import SpotGETTest
from spotseeker_server.test.no_rest_methods import NoRESTMethodsTest
from spotseeker_server.test.schema import SpotSchemaTest
from spotseeker_server.test.images.get import SpotImageGETTest
from spotseeker_server.test.images.post import SpotImagePOSTTest
from spotseeker_server.test.images.put import SpotImagePUTTest
from spotseeker_server.test.images.delete import SpotImageDELETETest
from spotseeker_server.test.images.thumb import ImageThumbTest
from spotseeker_server.test.images.spot_info import SpotResourceImageTest
from spotseeker_server.test.images.oauth_spot_info import (
    SpotResourceOAuthImageTest,
)
from spotseeker_server.test.item.model import ItemModelTest
from spotseeker_server.test.search.item import SpotSearchItemTest
from spotseeker_server.test.search.buildings import BuildingSearchTest
from spotseeker_server.test.search.uw_buildings import UWBuildingSearchTest
from spotseeker_server.test.search.capacity import SpotSearchCapacityTest
from spotseeker_server.test.search.limit import SpotSearchLimitTest
from spotseeker_server.test.search.distance import SpotSearchDistanceTest
from spotseeker_server.test.search.fields import SpotSearchFieldTest
from spotseeker_server.test.search.distance_fields import (
    SpotSearchDistanceFieldTest,
)
from spotseeker_server.test.search.view_methods import (
    SpotSearchViewMethodsTest,
)
from spotseeker_server.test.search.noise_level import NoiseLevelTestCase
from spotseeker_server.test.search.uw_noise_level import UWNoiseLevelTestCase
from spotseeker_server.test.search.time import SpotSearchTimeTest
from spotseeker_server.test.hours.model import SpotHoursModelTest
from spotseeker_server.test.hours.get import SpotHoursGETTest
from spotseeker_server.test.hours.put import SpotHoursPUTTest
from spotseeker_server.test.hours.post import SpotHoursPOSTTest
from spotseeker_server.test.hours.open_now import SpotHoursOpenNowTest
from spotseeker_server.test.hours.open_at import SpotHoursOpenAtTest
from spotseeker_server.test.hours.open_until import SpotHoursOpenUntilTest
from spotseeker_server.test.hours.hours_range import HoursRangeTest
from spotseeker_server.test.hours.open_now_location import (
    SpotHoursOpenNowLocationTest,
)
from spotseeker_server.test.hours.open_now_location_attributes import (
    SpotHoursOpenNowLocationAttributesTest,
)
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
from spotseeker_server.test.item.form import ItemFormsTest
from spotseeker_server.test.spot_caching import SpotCacheTest
from spotseeker_server.test.item.image_delete import ItemImageDELETETest
from spotseeker_server.test.item.image_get import ItemImageGETTest
from spotseeker_server.test.item.image_post import ItemImagePOSTTest
from spotseeker_server.test.item.image_put import ItemImagePUTTest
from spotseeker_server.test.item.image_thumbnail import ItemImageThumbTest
from spotseeker_server.test.techloan.sync_techloan import SyncTechloanTest
