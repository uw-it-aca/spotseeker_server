if [ "$ENV" = "localdev" ]
then

  python manage.py loaddata oauth.json

fi