from finance.core.models import Profile


class ProfileContextMiddleware(object):
    def process_template_response(self, request, response):
        if request.user.is_authenticated():
            profile = Profile.objects.get(user=request.user)
            response.context_data["profile"] = profile
        return response
