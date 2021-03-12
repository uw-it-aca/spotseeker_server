[![Build Status](https://github.com/uw-it-aca/spotseeker_server/workflows/Build%2C%20Test%20and%20Deploy/badge.svg?branch=master)](https://github.com/uw-it-aca/spotseeker_server/actions)
[![Coverage Status](https://coveralls.io/repos/github/uw-it-aca/spotseeker_server/badge.svg?branch=master)](https://coveralls.io/github/uw-it-aca/spotseeker_server?branch=master)

# SpaceScout Server

This is the server for the SpaceScout suite of applications. It stores space metadata and resources as well as provides services to the SpaceScout web and mobile apps.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

* Docker
* Docker-compose
* git
* JPEG libraries from [http://www.ijg.org/](http://www.ijg.org/) (Optional, but PIL will not support JPEG images without it.)


### Steps to run

First, clone the app:

    $ git clone https://github.com/uw-it-aca/spotseeker_server.git

If you wish to change the default settings, navigate to the develop branch and copy the sample environment variables into your own `.env` file:

    $ cd spotseeker_server
    $ git checkout develop
    $ cp sample.env .env

Then, run the following command to build your docker container:

    $ docker-compose up --build


#### Additional settings:

SPOTSEEKER_AUTH_MODULE setting can be one of 'all_ok' or 'oauth'. If using 'oauth', client applications will need an oauth key/secret pair. The 'all_ok' module is not suitable for production.

To find more information on how to set up the 'all_ok' Auth Module, check [here](https://github.com/uw-it-aca/spotseeker_server/wiki/Using-'all_ok'-oauth-module)

Custom validation can be added by adding SpotForm and ExtendedInfoForm to org_forms and setting them here. (For example, SPOTSEEKER_SPOT_FORM could be default.DefaultSpotForm or org_forms.UWSpotForm , SPOTSEEKER_SPOTEXTENDEDINFO_FORM could be org_forms.UWSpotExtendedInfoForm or default.DefaultSpotExtendedInfoForm, and SPOTSEEKER_SEARCH_FILTERS could contain or  org_filters.uw_search.Filter or org_filters.sample_search.Filter)

```
SPOTSEEKER_SPOT_FORM = 'spotseeker_server.org_forms.MODULE'
SPOTSEEKER_SPOTEXTENDEDINFO_FORM = 'spotseeker_server.org_forms.MODULE'
SPOTSEEKER_SEARCH_FILTERS = ('spotseeker_server.org_filters.MODULE', )
```

For additional settings, see [some page that doesn't exist.]

You can also optionally create some sample spot data:

```
python manage.py create_sample_spots
```

## Running the tests

    $ docker-compose run --rm app bin/python manage.py test

## Deployment

(To be completed.)

## Built With

* [Django](http://djangoproject.com/)

## Contributing

Please read [CONTRIBUTING.md] for details on our code of conduct, and the process for submitting pull requests to us. (This has yet to be writtien.)

## Versioning

For the versions available, see the [tags on this repository](https://github.com/uw-it-aca/spotseeker_server/tags).

## Authors

* [**Academic Experience Design & Delivery**](https://github.com/uw-it-aca)

See also the list of [contributors](https://github.com/uw-it-aca/spotseeker_server/contributors) who participated in this project.

## License

Copyright 2012-2016 UW Information Technology, University of Washington

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## List of settings

(To be moved to the wiki eventually.)

JSON_PRETTY_PRINT
SPOTSEEKER_AUTH_ADMINS
SPOTSEEKER_AUTH_MODULE
SPOTSEEKER_SEARCH_FILTERS
USER_EMAIL_DOMAIN
