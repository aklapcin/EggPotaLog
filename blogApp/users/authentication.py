from tastypie.authentication import Authentication
from tastypie.authorization import Authorization


class BlogAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        return request.user.is_authenticated()

    # Optional but recommended
    def get_identifier(self, request):
        if request.user.is_authenticated():
            return request.user.email
        else:
            return 'Anonymous'


class BlogAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        return True
