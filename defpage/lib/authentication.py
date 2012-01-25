import json
import base64
import httplib2
import binascii
from zope.interface import Interface
from zope.interface import Attribute
from zope.interface import implementer
from paste.httpheaders import AUTHORIZATION
from paste.httpheaders import WWW_AUTHENTICATE
from pyramid.security import authenticated_userid
from pyramid.security import Everyone
from pyramid.security import Authenticated
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.httpexceptions import HTTPUnauthorized
from defpage.lib.exceptions import ServiceCallError

def authenticate(event):
    user = event.request.registry.getUtility(IUser)
    user.authenticate(event.request)

def authenticated(func):
    def wrapper(req):
        if not authenticated_userid(req):
            raise HTTPUnauthorized
        return func(req)
    return wrapper

class IUser(Interface):
    """User info for authenticated user.
    """

    authenticated = Attribute("Boolean")

    user_id = Attribute("User id")

    def authenticate(request):
        """Update attributes in new request"""

@implementer(IUser)
class UserBase(object):

    authenticated = False
    user_id = None

    def authenticate(self, request, cookie_name, sessions_url):
        key = request.cookies.get(cookie_name)
        if key:
            url = sessions_url + key
            h = httplib2.Http()
            response, content = h.request(url)
            if response.status == 200:
                info = json.loads(content)
                self.user_id = info['user_id']
                self.authenticated = True
                self._authenticated(request, info)
                return
            elif response.status != 404:
                raise ServiceCallError
        self.authenticated = False
        self.user_id = None
        self._unauthenticated(request)

    def _authenticated(self, request, info):
        pass

    def _unauthenticated(self, request):
        pass

@implementer(IAuthenticationPolicy)
class SessionAuthenticationPolicy(object):

    def authenticated_userid(self, request):
        user = request.registry.getUtility(IUser)
        return user.user_id

    def unauthenticated_userid(self, request):
        return None

    def effective_principals(self, request):
        return [self.authenticated_userid(request)]

    def remember(self, request, principal, email):
        return []

    def forget(self, request):
        return []

def _get_basicauth_credentials(request):
    authorization = AUTHORIZATION(request.environ)
    try:
        authmeth, auth = authorization.split(' ', 1)
    except ValueError: # not enough values to unpack
        return None
    if authmeth.lower() == 'basic':
        try:
            auth = auth.strip().decode('base64')
        except binascii.Error: # can't decode
            return None
        try:
            login, password = auth.split(':', 1)
        except ValueError: # not enough values to unpack
            return None
        return {'login':login, 'password':password}
    return None

@implementer(IAuthenticationPolicy)
class BasicAuthenticationPolicy(object):
    """ A :app:`Pyramid` :term:`authentication policy` which
    obtains data from basic authentication headers.

    Constructor Arguments

    ``check``

        A callback passed the credentials and the request,
        expected to return None if the userid doesn't exist or a sequence
        of group identifiers (possibly empty) if the user does exist.
        Required.

    ``realm``

        Default: ``Realm``.  The Basic Auth realm string.

    """

    def __init__(self, check, realm='Realm'):
        self.check = check
        self.realm = realm

    def authenticated_userid(self, request):
        credentials = _get_basicauth_credentials(request)
        if credentials is None:
            return None
        userid = credentials['login']
        if self.check(credentials, request) is not None: # is not None!
            return userid

    def effective_principals(self, request):
        effective_principals = [Everyone]
        credentials = _get_basicauth_credentials(request)
        if credentials is None:
            return effective_principals
        userid = credentials['login']
        groups = self.check(credentials, request)
        if groups is None: # is None!
            return effective_principals
        effective_principals.append(Authenticated)
        effective_principals.append(userid)
        effective_principals.extend(groups)
        return effective_principals

    def unauthenticated_userid(self, request):
        creds = _get_basicauth_credentials(request)
        if creds is not None:
            return creds['login']
        return None

    def remember(self, request, principal, **kw):
        return []

    def forget(self, request):
        head = WWW_AUTHENTICATE.tuples('Basic realm="%s"' % self.realm)
        return head
