#!/bin/bash

if [ "$ENV" = "localdev" ]
then

  python manage.py migrate
  python manage.py loaddata dummy_oauth.json

fi