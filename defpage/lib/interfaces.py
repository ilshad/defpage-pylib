from zope.interface import Interface
from zope.interface import Attribute

class IUser(Interface):
    """User info for authenticated user.
    """

    authenticated = Attribute("Boolean")

    user_id = Attribute("User id")

    def authenticate(request):
        """Update attributes in new request"""
