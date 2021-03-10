from django.conf import settings
from django.shortcuts import redirect, reverse
from django.contrib import messages


class ClientAuthorizationMiddleware:
    """
    Users need to be authorized to access any page other than LOGIN_URL.

    https://docs.djangoproject.com/en/3.1/topics/http/middleware/#writing-your-own-middleware
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.login_url = settings.LOGIN_URL
        self.exempt_urls = [
            self.login_url,
            reverse('homepage'),
            reverse('logout'),
            reverse('django_registration_register'),
        ]

    def __call__(self, request):
        if not self.is_authorized(request.user):
            if request.path_info not in self.exempt_urls:
                messages.warning(request, 'Your account needs to be approved. '
                                          'Please contact you Account Manager.')
                return redirect(f'{self.login_url}?next={request.path}')

        return self.get_response(request)

    @staticmethod
    def is_authorized(user):
        return user.is_authenticated and user.is_approved
