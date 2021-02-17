FROM acait/django-container:1.0.38 as app-container

USER acait

ADD --chown=acait:acait setup.py /app/
ADD --chown=acait:acait requirements.txt /app/
ADD --chown=acait:acait requirements /app/requirements

RUN . /app/bin/activate && pip install -r requirements.txt

ADD --chown=acait:acait . /app/
ADD --chown=acait:acait docker/ project/

FROM acait/django-test-container:1.0.38 as app-test-container

COPY --from=0 /app/ /app/
COPY --from=0 /static/ /static/
