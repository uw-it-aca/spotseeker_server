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
from django.core.mail import EmailMultiAlternatives
from spotseeker_server.require_auth import user_auth_required
from spotseeker_server.models import Spot
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import get_template
from django.template import Context
import json
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
        except Exception as e:
            raise RESTException("Unable to parse JSON", status_code=400)

        if 'to' not in json_values:
            raise RESTException("Missing 'to'", status_code=400)

        send_to = json_values['to']
        if '@' not in send_to:
            raise RESTException("Invalid 'to'", status_code=400)

        comment = ''
        if 'comment' in json_values:
            comment = json_values['comment']

        log_message = "user: %s; spot_id: %s; recipient: %s; space suggested" % (user.username, spot.pk, send_to)
        logger.info(log_message)


        context = Context({
            'user_name': user.username,
            'space_name': spot.name,
            'space_url': spot.sharing_url(user_from = user),
            'comment': comment,
        })

        subject_template = get_template('email/share_space/subject.txt')
        text_template = get_template('email/share_space/plain_text.txt')
        html_template = get_template('email/share_space/html.html')

        subject = subject_template.render(context).rstrip()
        text_content = text_template.render(context)
        html_content = html_template.render(context)
        to = send_to
        from_email = getattr(settings, 'SPACESCOUT_SUGGEST_FROM', 'spacescout+noreply@uw.edu')
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return JSONResponse(True)
