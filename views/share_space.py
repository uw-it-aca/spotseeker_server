""" Copyright 2014 UW Information Technology, University of Washington

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

from spotseeker_server.views.rest_dispatch import RESTDispatch, JSONResponse, RESTException
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from spotseeker_server.require_auth import user_auth_required, app_auth_required
from spotseeker_server.models import Spot, SpotExtendedInfo
from spotseeker_server.models import SharedSpace, SharedSpaceRecipient
from spotseeker_server.auth.oauth import authenticate_user
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from django.utils.http import urlquote
from django.utils import timezone
import json
import socket
import re
import hashlib
import logging

logger = logging.getLogger(__name__)

class ShareSpaceView(RESTDispatch):
    """ Share a space, url at /api/v1/spot/<spot_id>/share."""
    @user_auth_required
    def PUT(self, request, spot_id):
        user = self._get_user(request)
        spot = Spot.objects.get(pk=spot_id)

        body = request.read()
        try:
            json_values = json.loads(body)
        except Exception:
            logger.error('Unable to parse JSON body: %s' % (body))
            raise RESTException("Unable to parse JSON", status_code=400)

        if 'to' not in json_values:
            logger.error('Missing To in JSON: %s' % (body))
            raise RESTException("Missing 'To'", status_code=400)

        raw_send_to = json_values['to']
        if type(raw_send_to) is not list:
            raw_send_to = [ raw_send_to ]

        has_valid_to = False
        send_to = []
        for address in raw_send_to:
            if '@' in address:
                send_to.append(address)
                has_valid_to = True

        if not has_valid_to:
            logger.error('Invalid To field:  %s' % (body))
            raise RESTException("Invalid 'To'", status_code=400)

        send_from = json_values['from'] if 'from' in json_values else None
        if send_from and '@' not in send_from:
            logger.error('Invalid From field:  %s' % (body))
            raise RESTException("Invalid 'from'", status_code=400)

        comment = ''
        if 'comment' in json_values:
            comment = json_values['comment']

        try:
            share = SharedSpace.objects.get(space=spot,sender=send_from,user=user.username)
        except ObjectDoesNotExist:
            share = SharedSpace(space=spot,sender=send_from,user=user.username)
            share.save()

        for to in send_to:
            try:
                server = getattr(settings, 'SS_APP_SERVER', socket.gethostname())
                path = getattr(settings, 'SS_APP_SPACE_PATH', '/space/{{ spot_id }}/{{ spot_name }}')
                path = re.sub(r'{{\s*spot_id\s*}}', spot_id, path)
                path = re.sub(r'{{\s*spot_name\s*}}', urlquote(spot.name), path)
                hash_val = hashlib.md5("%s|%s|%s" % (spot.pk, send_from, to)).hexdigest()
                share_url = "http://%s%s/%s" % (server, path, hash_val)
    
                try:
                    recipient = SharedSpaceRecipient.objects.get(hash_key=hash_val)
                    recipient.shared_count = recipient.shared_count + 1
                except ObjectDoesNotExist:
                    recipient = SharedSpaceRecipient(shared_space=share,hash_key=hash_val,
                                                    recipient=to,shared_count=1,viewed_count=0)

                recipient.save()

                location_description = None
                try:
                    location_description = SpotExtendedInfo.objects.get(spot=spot, key='location_description').value
                except ObjectDoesNotExist:
                    pass

                spottypes = spot.spottypes.all()
                spottypes = ["server_%s" % x for x in spottypes]

                context = Context({
                    'user_name': user.username,
                    'spot_name': spot.name,
                    'spot_type': spottypes,
                    'spot_building': spot.building_name,
                    'spot_location': location_description,
                    'spot_floor': spot.floor,
                    'share_url': share_url,
                    'comment': comment,
                })
    
                subject_template = get_template('email/share_space/subject.txt')
                text_template = get_template('email/share_space/plain_text.txt')
                html_template = get_template('email/share_space/html.html')
    
                subject = json_values['subject'] if 'subject' in json_values else subject_template.render(context).rstrip()
                text_content = text_template.render(context)
                html_content = html_template.render(context)
                from_email = getattr(settings, 'SPACESCOUT_SUGGEST_FROM', 'spacescout+noreply@uw.edu')
    
                headers = {}
                if send_from:
                    headers['Sender'] = getattr(settings, 'SPACESCOUT_SUGGEST_FROM', 'spacescout+noreply@uw.edu')
                    from_email = send_from
                else:
                    from_email = getattr(settings, 'SPACESCOUT_SUGGEST_FROM', 'spacescout+noreply@uw.edu')

                msg = EmailMultiAlternatives(subject, text_content, from_email, [to], headers=headers)
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except Exception as e:
                logger.exception('Share Send Failure: %s' % (e))
                raise RESTException("Cannot share space at this time: %s" % (e), status_code=500)

        return JSONResponse(True)


class SharedSpaceReferenceView(RESTDispatch):
    """ Record shared space reference"""
    @app_auth_required
    def PUT(self, request, spot_id):
        user = None
        try:
            authenticate_user(self, request)
            user = self._get_user(request)
        except:
            pass

        body = request.read()
        try:
            json_values = json.loads(body)
        except Exception:
            raise RESTException("Unable to parse JSON", status_code=400)

        if 'hash' not in json_values:
            raise RESTException("Missing 'hash'", status_code=400)

        try:
            recipient = SharedSpaceRecipient.objects.get(hash_key=json_values['hash'])
        except ObjectDoesNotExist:
            return JSONResponse("{error: 'shared spot not found'}", status=401)

        if recipient.shared_space.space.pk == int(spot_id):
            recipient.viewed_count = recipient.viewed_count + 1

            if not recipient.date_first_viewed:
                recipient.date_first_viewed = timezone.now()

            if user and user.username:
                recipient.user = user.username

            recipient.save()
        else:
            return JSONResponse("{error: 'spot mismatch'}", status=401)

        return JSONResponse(True)
