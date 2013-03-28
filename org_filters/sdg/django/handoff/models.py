#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/handoff/models.py $
#   $Revision: 29352 $ $Date: 2012-04-23 15:45:00 -0500 (Mon, 23 Apr 2012) $

#   Copyright (c) 2011 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

"""
Defines a model used to store information about sessions that are to be handed
off to a remote application for further processing. Remote application uses
handoff API to retrieve data stored here.
"""

import logging

from datetime import datetime, timedelta

from django.db import models

_PRUNE_DAYS_DEFAULT     = 7         # Default age for pruning.
_PRUNE_DAYS_MINIMUM     = 1         # Minimum age for pruning.

#####

class AnnouncedSession(models.Model):
    '''
    Model used to record announced sessions; this facilitates secure
    sharing of session data between applications.
    '''

    application_id      = models.CharField(max_length=32, 
                                           blank=False, null=False)

    session_private     = models.CharField(max_length=128, 
                                           blank=False, null=False)

    session_public      = models.CharField(max_length=128, 
                                           blank=False, null=False)

    is_completed        = models.BooleanField(blank=False, null=False,
                                              default=False)

    user_data           = models.TextField(blank=True, null=True)

    create_dt           = models.DateTimeField(auto_now_add=True)

    #####

    #   pylint: disable=C0111,W0232
    class Meta:
        db_table        = 'sdg_announced_session'
        unique_together = ('application_id', 'session_private')

    #####

    @classmethod
    def prune(cls, days=_PRUNE_DAYS_DEFAULT):
        '''
        Prune model by discarding rows older than specified age.
        '''

        days = abs(days)

        #   Enforce minimum delta.
        if days < _PRUNE_DAYS_MINIMUM:
            raise ValueError \
                    ('can not prune data < %d day old.', _PRUNE_DAYS_MINIMUM)

        #   Compute compare_dt based on current time and desired delta.
        compare_dt = datetime.now() - timedelta(days)

        #   Form queryset.
        #   pylint: disable=E1101
        queryset = cls.objects.filter(create_dt__lt=compare_dt)

        #   Count rows in queryset and delete; count is returned to caller.
        count = queryset.count()

        if count:
            queryset.delete()
            logging.info('deleted %d %s rows', count, cls.__name__)

        return count
