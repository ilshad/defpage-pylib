import json
import httplib2
from zope.interface import implementer
from pyramid.interfaces import IAuthenticationPolicy
from defpage.lib.exceptions import ServiceCallError

def authenticate(event):
    user = event.request.registry.getUtility(IUser)
    user.authenticate(event.request)

class UserBase(object):

    authenticated = False
    user_id = None

    def authenticate(self, request, cookie_name, session_url):
        key = request.cookies.get(cookie_name)
        if key:
            url = sessions_url + key
            h = httplib2.Http()
            response, content = h.request(url)
            if response.status == 200:
                info = json.loads(content)
                self.user_id = info['user_id']
                self.authenticated = True
                self._auhenticated(request, info)
                return
            elif response.status != 404:
                raise ServiceCallError
        self.authenticated = False
        self.user_id = None
        self._unauhenticated(request, info)

    def _authenticated(self, request, info):
        pass

    def _unauthenticated(self, request, info):
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
