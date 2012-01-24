import json
import base64
import httplib2
from zope.interface import Interface
from zope.interface import Attribute
from zope.interface import implementer
from pyramid.security import authenticated_userid
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.httpexceptions import HTTPUnauthorized
from defpage.lib.exceptions import ServiceCallError

def authenticate(event):
    user = event.request.registry.getUtility(IUser)
    user.authenticate(event.request)

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

@implementer(IAuthenticationPolicy)
class BasicAuthenticationPolicyBase(object):

    def extract_credentials(self, request):
        h = request.headers.get("authorization")
        if h.startswith("basic "):
            credentials = h.split()[-1]
            return base64.b64decode(credentials).split(":")

    def authenticated_userid(self, request):
        raise NotImplementedError

    def unauthenticated_userid(self, request):
        return self.extract_credentials(request)

    def effective_principals(self, request):
        return [self.authenticated_userid(request)]

    def remember(self, request, principal, email):
        return []

    def forget(self, request):
        return []

def authenticated(func):
    def wrapper(req):
        if authenticated_userid(req):
            raise HTTPUnauthorized
        return func(req)
    return wrapper
