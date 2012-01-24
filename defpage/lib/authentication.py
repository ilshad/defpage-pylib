import json
import httplib2
from zope.interface import Interface
from zope.interface import Attribute
from zope.interface import implementer
from pyramid.interfaces import IAuthenticationPolicy
from defpage.lib.exceptions import ServiceCallError
from defpage.lib.interfaces import IUser

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
class AuthenticationPolicy(object):

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
