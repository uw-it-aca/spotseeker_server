# SpaceScout Server

This is the server for the SpaceScout suite of applications. It stores space metadata and resources as well as provides services to the SpaceScout web and mobile apps.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

* Django <1.4.
* A Python installation (2.6 or 2.7)
* pip or easy_install
* git
* JPEG libraries from [http://www.ijg.org/](http://www.ijg.org/) (Optional, but PIL will not support JPEG images without it.)


### Installing

Use pip to install the app as editable from GitHub:

```
pip install -e git+https://github.com/uw-it-aca/spotseeker_server.git#egg=spacescout-server
```

Enable the RemoteUserBackend:

```
MIDDLEWARE_CLASSES = (
    ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    ...
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.RemoteUserBackend',
)
```

Add spotseeker_server to your INSTALLED_APPS in settings.py:

```
INSTALLED_APPS = (
    ...
    'oauth_provider',
    'spotseeker_server',
    ...
)
```

Add the app to your project's urls.py:

```
urlpatterns = patterns('',
...
    url(r'^auth/', include('oauth_provider.urls')),
    url(r'^api/', include('spotseeker_server.urls')),
...
)
```

Additional settings:

MODULE can be one of 'all_ok' or 'oauth'. If using 'oauth', client applications will need an oauth key/secret pair. The 'all_ok' module is not suitable for production.

```
SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.MODULE'
```

A list or tuple of usernames allowed to use methods that modify server data (PUT, POST, DELETE.)

```
SPOTSEEKER_AUTH_ADMINS = []
```

Custom validation can be added by adding SpotForm and ExtendedInfoForm to org_forms and setting them here. (For example, in the spot form, MODULE could be default.DefaultSpotForm or org_forms.UWSpotForm.)

```
SPOTSEEKER_SPOT_FORM = 'spotseeker_server.org_forms.MODULE'
SPOTSEEKER_SPOTEXTENDEDINFO_FORM = 'spotseeker_server.org_forms.MODULE'
```

Create your database, and you can run the server.

```
python manage.py syncdb
python manage.py runserver
```

You can also optionally create some sample spot data:

```
python manage.py create_sample_spots
```

## Running the tests

```
python manage.py test spotseeker_server
```

## Deployment

(To be completed.)

## Built With

* [Django](http://djangoproject.com/)

## Contributing

Please read [CONTRIBUTING.md] for details on our code of conduct, and the process for submitting pull requests to us.

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
