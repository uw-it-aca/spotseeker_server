#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/handoff/_wsapi.py $
#   $Revision: 31466 $ $Date: 2012-07-30 12:53:03 -0500 (Mon, 30 Jul 2012) $

#   Copyright (c) 2011 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''
Package of SDG functions related to handing off one web application to another
under Django.
'''

__all__ = \
    [
    'models',
    ]

import logging

from sdg import standard_path

import hmac
import simplejson as json
import sys
import types

from httplib import HTTPConnection, HTTPSConnection
from types import DictType
from urlparse import urlparse, urlunparse

from django.db import transaction
from django.http import HttpResponse

from sdg import hexdigest
from sdg import log

from sdg.django.handoff.models import AnnouncedSession

#   Initialize module logger.
LOGGER = log.init_module_logger()

#####

class WSAPI(object):

    _ENCODED_MIME_TYPE  = 'text/json'

    #####

    class WSAPIError(Exception):
        '''Class from which other WSAPI errors inherit.'''
        pass

    #####

    class DataIntegrityError(WSAPIError):
        '''Raised when transferred data fails integrity test.'''
        pass

    #####

    class KeyIntegrityError(WSAPIError):
        '''Raised when public key fails integrity test.'''
        pass

    #####

    class ProtocolError(WSAPIError):
        '''Raised when invoked incorrectly.'''
        pass

    #####

    class UnknownMethodError(WSAPIError):
        '''Raised when invoked method doesn\'t exist.'''
        pass

    #####

    class UnknownSessionError(WSAPIError):
        '''Raised when referencing unknown or invalid session.'''
        pass

    #####

    def __init__(self, service_secret_path=None):
        if not service_secret_path:
            raise KeyError('service_secret_path not specified')

        self.application_id         = None
        self.service_secret_path    = service_secret_path
        self.session_private        = None
        self.session_public         = None
        return None
    
    #####

    def _generate_verification_hash(self, data):
        '''Generate hash to verify that data wasn't tampered with en route.'''

        flat_list = list(WSAPI.flatten(data))
        return self._hash_with_service_secret(*flat_list)

    #####

    def _hash_with_service_secret(self, *arg_list):
        '''Hashes arguments with the shared service secret.'''
    
        try:
            service_secret = hexdigest.read_hexdigest(self.service_secret_path)

            hash = hmac.new(service_secret, digestmod=hexdigest.HASH_CLASS)
            [ hash.update(a) for a in arg_list ]

        except Exception, x:
            import traceback
            log.log_exception()
            logging.error('self: %s' % self.classname())
        #   logging.error('service_secret: %s' % service_secret)
            logging.error('arg_list: %s (%s)' % (str(arg_list), type(arg_list)))
            raise
    
        return hash.hexdigest()

    #####

    def classname(self):
        '''Returns name of object's class.'''

        return self.__class__.__name__

    #####

    @staticmethod
    def decode(data):
        '''Decode data from.'''
        return json.JSONDecoder().decode(data)

    #####

    def django_key(self):
        '''Derives key used in Django session model from application id.'''
        return 'WSAPI_%s' % (self.application_id)
    
    #####

    @staticmethod
    def encode(data):
        '''Encode data.'''
        return json.JSONEncoder().encode(data)

    #####

    @staticmethod
    def flatten(obj):
        '''Flatten arbitrarily deep object.'''

        #   If not iterator, simply return object.
        if not hasattr(obj, '__iter__'):
            yield obj
            return

        #   Dictionaries require special handling so that their members are
        #   returned in deterministic order.
        if isinstance(obj, DictType):
            #   Sort dictionary.
            for key, value in sorted(obj.items()):
                yield key
                #   Recursively call generator; iterate over generated values.
                for v in WSAPI.flatten(value):
                    yield v
            return

        #   Handle regular iterable.
        for sublist in obj:
            for element in WSAPI.flatten(sublist):
                yield element
        return

#####

class WSAPIAnnouncer(WSAPI):

    #####

    def __init__(self, **kw_arg_dict):
        if not 'application_id' in kw_arg_dict:
            raise KeyError('application_id not specified')

        application_id = kw_arg_dict.pop('application_id')

        super(WSAPIAnnouncer, self).__init__(**kw_arg_dict)

        #   Save application ID.
        self.application_id     = application_id

        #   Generate private and public key pair.
        self.session_private    = hexdigest.generate_hexdigest()
        self.session_public     = self._hash_with_service_secret \
                                    (self.session_private)
        return None

    #####

    def announce(self, request=None, user_data=None):
        '''
        Announce session by writing its pertinent information to
        AnnouncedSession model. Uses Django request object.
        '''

        if not request:
            raise KeyError('request not specified')

        #   Populate an AnnouncedSession object.
        announced_session = AnnouncedSession \
            (
            application_id=self.application_id,
            session_private=self.session_private,
            session_public=self.session_public,
            user_data=WSAPI.encode(user_data)
            )

        #   Commit model.
        announced_session.save()

        #   Write primary key of announced session to Django session object.
        dkey = self.django_key()
        request.session[dkey] = announced_session.pk

        logging.debug('%s: announce: session public: %s (%s)' % \
                      (self.classname(), self.session_public, dkey))
        return None

#####

class WSAPIClient(WSAPI):

    #####

    def __init__(self, **kw_arg_dict):
        if not 'application_id' in kw_arg_dict:
            raise KeyError('application_id not specified')

        #   Extract application id and call superclass constructor.
        application_id = kw_arg_dict.pop('application_id')

        super(WSAPIClient, self).__init__(**kw_arg_dict)

        #   Save application ID.
        self.application_id     = application_id

        return None

    #####

    def _check_response(self, method_name, resp_body):
        '''Called by client to check whether server has exception to handle.'''

        #   If response object isn't a dictionary, or doesn't have a key
        #   named 'exception', this isn't an exception, so we return.
        if not isinstance(resp_body, DictType) or 'exception' not in resp_body:
            return

        #   Extract components from exception tuple.
        name, message, arg_list = resp_body['exception'][:]

        import exceptions

        #   Iterate over modules likely to contain pertinent exception classes.
        for cls in (WSAPI, exceptions):
            #   Skip module without attribute matching exception name.
            if not hasattr(cls, name):
                continue

            #   Get class object from matching attribute.
            exc_class = getattr(cls, name)

            #   Validate that constructed object is an instance of the
            #   Exception object.
            if not isinstance(exc_class(), Exception):
                logging.error('%s: server returned bogus exception %s' % \
                              (self.classname(), name))
                break

            logging.error('%s: method \'%s\' exception: %s' % \
                          (self.classname(), method_name, name))

            #   If arguments supplied, use them while raising exception.
            if len(arg_list):
                raise exc_class(arg_list)

            #   Otherwise, use [possibly-empty] message while raising exception.
            else:
                raise exc_class(message)
            
        #   Couldn't identify exception
        logging.error('%s: unidentified exception from server: %s (%s)' % \
                      (self.classname(), name, 
                       str(arg_list) if len(arg_list) else message))
        raise Exception('Unidentified exception from server')

    #####
    
    def _recv_raw_response(self, url, method_name, req_body):
        '''Called by client to make HTTP POST request and process response.'''

        logging.debug('%s: method \'%s\' request: %s' % \
                      (self.classname(), method_name, str(req_body)))

        #   Parse URL and extract netloc and path.

        url_parsed = urlparse(url)

        netloc = url_parsed.netloc
    
        #   Append method name to base path.
        path   = url_parsed.path + method_name + '/'
    
        #   Set content type for POST.
        header_dict  = { 'Content-type' : WSAPI._ENCODED_MIME_TYPE }
    
        #   Generate verification hash.
        req_vfy = self._generate_verification_hash(req_body)

        #   Encode verification hash and request body.
        request_data = WSAPI.encode((req_vfy, req_body))

        #   Determine which URL scheme to instantiate.
        if url_parsed.scheme == 'http':
            http_class = HTTPConnection

        else:
            http_class = HTTPSConnection

        #   Make connection and issue HTTP POST request.
        conn = http_class(url_parsed.netloc)
    
        conn.request('POST', path, request_data, header_dict)

        url_unparsed = urlunparse \
                            ((url_parsed.scheme, url_parsed.netloc, path,
                              '', '', ''))
        logging.debug('%s: HTTP request (POST): \'%s\' data: %s' % \
                      (self.classname(), url_unparsed, request_data))
    
        #   Get HTTP response.
        resp = conn.getresponse()

        logging.debug('%s: HTTP response: %s %s' % \
                      (self.classname(), resp.status, resp.reason))

        #   Raise exception if request failed.
        if resp.status != 200:
            logging.debug(resp.read())
            raise Exception(resp.reason)

        #   Raise exception if incorrect content type.
        if resp.getheader('Content-type') != WSAPI._ENCODED_MIME_TYPE:
            raise Exception('incorrect content type')

        #   Read response data and decode into Python object.
        resp_raw = resp.read()
        return resp_raw

    #####
    
    def _request(self, url, method_name, req_body):
        '''Called by client to make HTTP POST request and process response.'''

        resp_raw = self._recv_raw_response(url, method_name, req_body)

        resp_data = self.decode(resp_raw)

        resp_vfy, resp_body = resp_data[:]

        if resp_vfy != self._generate_verification_hash(resp_body):
            raise WSAPI.DataIntegrityError \
                ('error decoding method \'%s\' response' % method_name)

        #   Handle exception (without returning) if response is dictionary
        #   and contains key named 'exception',
        self._check_response(method_name, resp_body)

        logging.debug('%s: method \'%s\' response: %s' % \
                      (self.classname(), method_name, str(resp_body)))

        return resp_body

    #####
    
    def retrieve(self, url, session_public):
        '''Called by client to retrieve data for announced session'''

        req_body = \
            {
            'application_id'    : self.application_id,
            'session_public'    : session_public,
            }

        session_private, user_data = self._request(url, 'retrieve', req_body)

        #   Recompute public key to verify response; raise exception on
        #   verification failure.
        if session_public != self._hash_with_service_secret(session_private):
            raise WSAPI.KeyIntegrityError

        return user_data

#####

class WSAPIServer(WSAPI):

    #####

    def _recv_raw_request(self, request):
        '''
        Called by server to process HTTP post request, invoke API call, and
        process response. Uses Django request object.
        '''

        #   Request method must be POST.
        if request.method != 'POST':
            raise WSAPI.ProtocolError \
                ('request method must be POST; was %s' % request.method)
    
        #   Request must have use proper MIME type.
        if request.META['CONTENT_TYPE'] != WSAPI._ENCODED_MIME_TYPE:
            raise WSAPI.ProtocolError \
                ('content type must be %s; was %s' % \
                    (WSAPI._ENCODED_MIME_TYPE, request.META['CONTENT_TYPE']))

        #   All's well; return raw POST data.
        return request.raw_post_data

    #####

    @transaction.commit_on_success
    def _handle_retrieve(self, req_dict):
        #   Determine whether required dictionary keys are present.
        if 'application_id' not in req_dict or 'session_public' not in req_dict:
            raise WSAPI.ProtocolError \
                ('application_id or session_public keys not specified')

        #   Extract required dictionary keys and raise exception if extraneous
        #   keys are present.
        application_id = req_dict.pop('application_id')
        session_public = req_dict.pop('session_public')
        
        if len(req_dict):
            raise WSAPI.ProtocolError \
                ('extraneous keys present: %s' % ', '.join(req_dict))

        #   Fetch matching AnnouncedSession object.
        try:
            a_session = AnnouncedSession.objects.get \
                            (application_id=application_id,
                             session_public=session_public,
                             is_completed=False)

        #   Raise exception if session doesn't exist
        except AnnouncedSession.DoesNotExist, x:
            raise WSAPI.UnknownSessionError \
                ('no session with session_public: %s' % session_public)
    
        #   Flag session as completed so subsequent callers can't retrieve it.
        a_session.is_completed = True
        a_session.save()

        #   Result consists of session private key and decoded user data
        #   from database.
        return a_session.session_private, WSAPI.decode(a_session.user_data)

    #####
    
    _method_dict = \
        {
        'retrieve'      : _handle_retrieve,
        }

    #####

    def serve(self, request, method_name):
        '''Handle request to server.'''

        try:
            #   Decode request from Django request object.
            req_data = WSAPI.decode((self._recv_raw_request(request)))

            #   Decoded data consists of 2-tuple; extract verification hash
            #   and data body.
            req_vfy, req_body = req_data[:]
        
            #   Recompute verification hash to verify message integrity.
            if req_vfy != self._generate_verification_hash(req_body):
                raise WSAPI.DataIntegrityError \
                    ('while decoding \'%s\' request' % method_name)

            #   Raise exception if unknown method invoked.
            if method_name not in WSAPIServer._method_dict:
                raise WSAPI.UnknownMethodError \
                    ('method \'%s\' doesn\'t exist' % method_name)

            #   Get handler object for specified method.
            method = WSAPIServer._method_dict[method_name]

            logging.debug('%s: method \'%s\' request: %s' % \
                          (self.classname(), method_name, str(req_body)))

            #   Invoke method.
            resp_body = method(self, req_body)

            logging.debug('%s: method \'%s\' response: %s' % \
                          (self.classname(), method_name, str(resp_body)))

        #   If WSAPIError encountered, build exception object for response.
        except WSAPI.WSAPIError, x:
            logging.error('%s: method \'%s\' exception: %s' % \
                          (self.classname(), method_name,
                           x.__class__.__name__))
            #   Build exception object and fall through.
            resp_body = \
                {
                'exception' : (x.__class__.__name__, x.message, x.args)
                }

        #   Other exceptions are logged and re-raised.
        except Exception, x:
            logging.error('%s: method \'%s\' exception: %s' % \
                          (self.classname(), method_name,
                          x.__class__.__name__))
            raise

        #   Generate verification hash from response body.
        resp_vfy = self._generate_verification_hash(resp_body)
    
        #   Encode verification hash and response body to be sent to caller.
        return WSAPI.encode((resp_vfy, resp_body))

    #####

    def serve_to_response(self, request, method_name):
        '''Handle request to server and generate HttpResponse for response.'''

        return HttpResponse(self.serve(request, method_name), 
                            mimetype=WSAPI._ENCODED_MIME_TYPE)
