FROM gcr.io/uwit-mci-axdd/django-container:1.3.8 as app-container

USER root
RUN apt-get update && apt-get install mysql-client libmysqlclient-dev -y
USER acait

ADD --chown=acait:acait setup.py /app/
ADD --chown=acait:acait requirements.txt /app/
ADD --chown=acait:acait requirements /app/requirements

RUN . /app/bin/activate && pip install -r requirements.txt
RUN . /app/bin/activate && pip install mysqlclient django-prometheus==2.0.0

ADD --chown=acait:acait . /app/
ADD --chown=acait:acait docker/ project/
COPY --chown=acait:acait docker/test_settings.py project/test_settings.py

FROM gcr.io/uwit-mci-axdd/django-test-container:1.3.8 as app-test-container

COPY --from=0 /app/ /app/
COPY --from=0 /static/ /static/
