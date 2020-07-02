FROM acait/django-container:1.0.31

USER acait

ADD --chown=acait:acait setup.py /app/
ADD --chown=acait:acait requirements.txt /app/
ADD --chown=acait:acait requirements /app/requirements

RUN . /app/bin/activate && pip install -r requirements.txt

ADD --chown=acait:acait spotseeker_server/ /app/spotseeker_server
ADD --chown=acait:acait docker/ project/