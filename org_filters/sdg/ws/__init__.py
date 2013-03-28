#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/ws/__init__.py $
#   $Revision: 32490 $ $Date: 2012-10-10 12:05:38 -0500 (Wed, 10 Oct 2012) $

#   Copyright (c) 2012 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''
Package of SDG functions related to handing off one web application to another
under Django.
'''

import hmac
import inspect
import json
import logging
import os
import pickle
import sys
import types

from httplib import HTTPConnection, HTTPSConnection
from types import DictType
from urlparse import urlparse, urlunparse, urljoin

#   pylint: disable=E0611
from sdg import standard_path
from sdg import log

#   Initialize module logger.
LOGGER = log.init_module_logger()

#####

class WebServiceError(Exception):
    '''Class from which other WebService errors inherit.'''
    pass

#####

class APIMethodError(WebServiceError):
    '''
    Raised by API methods when encountering problems with request that
    preclude successful processing.
    '''
    pass

#####

class ProtocolError(WebServiceError):
    '''
    Raised when API invoked incorrectly. Servers raise if HTTP
    request method is not POST, or if HTTP request contains
    improper content type. Clients raise for HTTP response other 
    than 200 OK, or improper content type in HTTP response.
    '''
    pass

#####

class ServerError(WebServiceError):
    '''Raised when unexpected exception is raised by an API method.'''
    pass

#####

class UnknownMethodError(WebServiceError):
    '''Raised when invoked API method doesn't exist.'''
    pass

#####

#   pylint: disable=R0903
class WebService(object):
    '''Implements a generic web service client/server interface.'''

    _data_key   = u'_data'
    _fault_key  = u'_fault'

    _required_class_attr_list = \
        [
        'content_type',
        'decode',
        'encode',
        ]

    #####

    def __init__(self, svc_class):
        #   Service class must be subclass of WebService but not WebService
        #   itself.
        if not issubclass(svc_class, WebService) and svc_class != WebService:
            raise Exception('class %s must be subclass of WebService' % \
                            svc_class.__name__)

        self.svc_class  = svc_class
        
        #   Check for required attributes missing.
        for attr in self._required_class_attr_list:
            #   pylint: disable=W0212
            if attr not in svc_class._class_attr_list:
                raise Exception \
                    ('required service class attribute \'%s\' missing for %s' %
                     (attr, svc_class.__name__))

            #   pylint: disable=W0212
            setattr(self, attr, svc_class._class_attr_list[attr])

    #####

    @staticmethod
    def _get_namespace():
        '''
        Returns reference to module from which invoked; used to manage
        distinct API "namespaces" when used by multi-view Django applications.
        '''
        frame  = inspect.stack()[2]
        module = inspect.getmodule(frame[0])
        return module

    #####

    def classname(self):
        '''Returns name of object's class.'''

        return self.__class__.__name__

#####

class ClientResponse(object):
    '''ClientResponse object containing fault or response data.'''
    
    #####

    def __init__(self, response_dict):
        '''Construct ClientResponse object. Used internally by Client class.'''

        self.data  = None
        self.fault = None

        #   pylint: disable=W0212
        fault = response_dict.get(WebService._fault_key, None)

        if not fault:
            #   pylint: disable=W0212
            self.data = response_dict.get(WebService._data_key)
            return

        self.fault = pickle.loads(str(fault))
        return

    #####

    def __str__(self):
        if self.is_fault:
            return '<fault:%s>' % self.fault

        return '<data:%s>' % self.data

    #####

    def is_fault(self):
        '''Returns Boolean indicating whether API method produced a fault.'''
        return self.fault is not None

#####

class Client(WebService):
    '''Base class for a web service client.'''

    #####

    def __init__(self, url, svc_class, **kw_arg_dict):
        self.doraise = kw_arg_dict.pop('doraise', True)

        super(self.__class__, self).__init__(svc_class, **kw_arg_dict)
        self.url = url

        #   Parse URL and extract netloc and path.
        self.url_parsed = urlparse(self.url)

        #   Set content type for POST.
        #   pylint: disable=E1101
        self.header_dict  = { 'Content-type' : self.content_type }
    
        #   Determine which URL scheme to instantiate.
        #   pylint: disable=E1101
        if self.url_parsed.scheme == 'http':
            self.http_class = HTTPConnection

        else:
            self.http_class = HTTPSConnection

        return 

    #####

    def __str__(self):
        '''Generate string rendition of object.'''
        return '[%s]' % self.url

    #####

    def request(self, method_name, api_request_object):
        '''
        Submit a request to the web service and process success or failure.
        '''

        #   pylint: disable=E1101
        request_encoded = self.encode(api_request_object)
    
        #   Append method name to base path.
        #   pylint: disable=E1101
        path = '/'.join((self.url_parsed.path, method_name, ''))
    
        try:
            #   pylint: disable=E1101
            url_unparsed = urlunparse \
                ((self.url_parsed.scheme, self.url_parsed.netloc, path,
                  '', '', ''))

            LOGGER.debug('%s: HTTP request (POST) to %s',
                         self.classname(), url_unparsed)

            #   Make connection and issue HTTP POST request.
            #   pylint: disable=E1101
            http_conn = self.http_class(self.url_parsed.netloc)
    
            http_conn.request('POST', path, request_encoded, self.header_dict)

        except:
            #   Construction of HTTP/HTTPS object failed, or request failed.
            #####   FIXME: Improve handling of transport faults, but let
            #####   caller handle.
        #   log.log_exception()
            raise

        #   Get HTTP response.
        http_response = http_conn.getresponse()

        LOGGER.debug('%s: HTTP response from %s (%s %s)',
                     self.classname(), url_unparsed, 
                     http_response.status, http_response.reason)

        try:
            self._validate_response(http_response)

            #   Read response data and decode into Python object.
            response_encoded = http_response.read()
    
            client_response = ClientResponse(self.decode(response_encoded))
    
            #   If response object has a fault key, this indicates the server
            #   method generated a fault. If doraise is true, we re-raise the
            #   exception for the caller to handle in a try/except block.
            #   Otherwise, fault is handled manually by the client using the
            #   client_response.fault attribute.
            #   pylint: disable=E0702
            if client_response.is_fault() and self.doraise:
                raise client_response.fault

        #   Unpickling error may be raised in ClientResponse contstructor.
        except pickle.UnpicklingError:
            #   Unable to unpickle fault object from server.
            log.log_exception('unable to unpickle server fault')
            raise

        #   Error validating or decoding response.
        except Exception:
            log.log_exception('error validating or decoding server response')
            raise

        return client_response

    #####

    def _validate_response(self, http_response):
        '''
        Called by serve() to validate HTTP request. Uses Django request object.
        '''

        #   Check that response returned OK status.
        if http_response.status != 200:
            #   Log response and raise exception if response wasn't 200 OK.
            LOGGER.debug(http_response.read())
            raise ProtocolError('received HTTP response %s %s' %
                                (http_response.status, http_response.reason))

        #   Raise exception if incorrect content type.
        content_type = http_response.getheader('Content-type')

        #   pylint: disable=E1101
        if content_type != self.content_type:
            #   Raise exception if incorrect content type.
            #   pylint: disable=E1101
            raise ProtocolError \
                    ('incorrect content type: got %s instead of expected %s' %
                     (content_type, self.content_type))

        return

#####

class Server(WebService):
    '''
    Base class for a web service that handles API requests to a web service.
    '''

    #   Dictionary of namespaces, which in turn contain dictionaries of methods.
    _api_namespace_dict = dict()

    #####

    #   pylint: disable=R0903
    class Decorator(object):
        '''Decorator class.'''

        #####

        @staticmethod
        def api_method(api_method_name=None):
            '''Decorator to identify public API method definition.'''
    
            #####

            def decorator(func):
                '''Outer closure that wraps inner clousure.'''
        
                #####

                def wrapped(*arg_list, **kw_arg_dict):
                    '''Inner closure to wrap specified API function.'''
                    return func(*arg_list, **kw_arg_dict)
        
                #   If api_method_name specified, expose API method by that
                #   name to client; otherwise use native function name.
                if api_method_name:
                    name = api_method_name

                else:
                    name = func.func_name

                #   pylint: disable=W0212
                namespace = WebService._get_namespace()
                
                #   pylint: disable=W0212
                if not namespace in Server._api_namespace_dict:
                    Server._api_namespace_dict[namespace] = dict()
                    
                #   Silently ignore any already-defined function by this name.
                Server._api_namespace_dict[namespace][name] = func

                return wrapped
        
            return decorator

    #####

    def __str__(self):
        '''Generate string rendition of object.'''
        return '[%s@%x]' % (self.__class__.__name__, id(self))

    #####

    @staticmethod
    def _format_remote_client(request):
        '''Formats data elements on remote client for log messages.'''

    #   request.META['REQUEST_URI']
        host = request.META.get('REMOTE_HOST', request.META.get('REMOTE_ADDR'))
        port = request.META.get('REMOTE_PORT', None)
        user = request.META.get('REMOTE_USER', 'anonymous')
        return '[%s@%s%s]' % (user, host, ':' + port if port else '')

    #####

    def _process_api_exception(self, request, exc, user_exception=None):
        '''Handle exception raised within API method.'''

        log.log_exception()
        LOGGER.info('%s: %s %s exception response to %s', 
                    self.classname(), request.path, 
                    exc.__class__.__name__, 
                    self._format_remote_client(request))

        try:
            if user_exception:
                exc_pickle = pickle.dumps(user_exception)

            else:
                exc_pickle = pickle.dumps(exc)

        #   pylint: disable=W0703
        except Exception:
            log.log_exception('error pickling exception')
            exc_pickle = pickle.dumps(ServerError('server error'))

        return { WebService._fault_key : exc_pickle }

    #####

    def serve(self, request, method_name):
        '''
        Handle API request. Uses Django request object and method name
        returned by Django URL dispatcher.
        '''

        LOGGER.info('%s: %s request from %s', 
                    self.classname(), request.path, 
                    self._format_remote_client(request))

        #   Validate request; will raise ProtocolError on failure.
        self._validate_request(request)

        try:
            #   Decode request from Django api_request_object object.
            #   pylint: disable=E1101
            api_request_object = self.decode(request.raw_post_data)
    
            namespace = WebService._get_namespace()

            #   Raise exception if unknown method invoked.
            if namespace not in self._api_namespace_dict:
                #   Falls through to first except clause.
                LOGGER.info('api method \'%s\' doesn\'t exist', method_name)
                raise UnknownMethodError \
                    ('api method \'%s\' doesn\'t exist' % method_name)

            method_dict = self._api_namespace_dict[namespace]

            if method_name not in method_dict:
                #   Falls through to first except clause.
                LOGGER.info('api method \'%s\' doesn\'t exist', method_name)
                raise UnknownMethodError \
                    ('api method \'%s\' doesn\'t exist' % method_name)
        
            #   Get handler object for specified method.
            method = method_dict[method_name]

            #   Invoke API method.
            api_response_object = method(self, api_request_object)

        except WebServiceError as exc:
            api_response_object = self._process_api_exception(request, exc)

        except Exception as exc:
            user_exception = \
                ServerError('error in server method \'%s\'' % method_name)
            api_response_object = self._process_api_exception \
                (request, exc, user_exception=user_exception)

        else:
            api_response_object = { WebService._data_key : api_response_object }
            LOGGER.info('%s: %s success response to %s', 
                         self.classname(), request.path, 
                         self._format_remote_client(request))

        #   Encode response for return to client.
        #   xxx pylint: disable=E1101
        return self.encode(api_response_object)

    #####

#   def serve_to_response(self, request, method_name):
#       '''
#       Serve API request and generate Django HttpResponse with server response.
#       '''
#       from django.http import HttpResponse
#
#       #   Create Django HttpResponse object with encoded server response.
#       #   pylint: disable=E1101
#       return HttpResponse(self.serve(request, method_name), 
#                           contenttype=self.content_type)
    
    #####

    def _validate_request(self, request):
        '''
        Called by serve() to validate HTTP request. Uses Django request object.
        '''

        #   Request method must be POST.
        if request.method != 'POST':
            raise ProtocolError \
                    ('incorrect request method: got %s instead of POST' % 
                     request.method)
    
        #   Request must have use proper MIME type.
        #   pylint: disable=E1101
        if request.META['CONTENT_TYPE'] != self.content_type:
            raise ProtocolError \
                    ('incorrect content type: got %s instead of expected %s' %
                     (self.content_type, request.META['CONTENT_TYPE']))

        return

#####

#   pylint: disable=R0903
class JSONWebService(WebService):
    '''Define a web service using JSON encoding.'''

    _class_attr_list = \
        {
        'content_type'  : 'text/json',
        'decode'        : json.JSONDecoder().decode,
        'encode'        : json.JSONEncoder().encode,
        }
