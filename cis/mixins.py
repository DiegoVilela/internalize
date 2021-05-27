from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages


class UserApprovedMixin(UserPassesTestMixin):
    """
    Deny access to unapproved users.
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_approved


class AddClientMixin:
    """
    Add the client to be saved on create views.

    Override form_valid() of CreateView.
    https://docs.djangoproject.com/en/stable/topics/class-based-views/generic-editing/#models-and-request-user
    """
    def form_valid(self, form):
        form.instance.client = self.request.user.client
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            messages.warning(request, 'Please use the admin area.')

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None  # As per `BaseCreateView`

        form = self.get_form()
        if form.is_valid():
            if request.user.is_superuser:
                messages.error(request, 'Please use the admin area.')
                return self.form_invalid(form)

            return self.form_valid(form)
        else:
            return self.form_invalid(form)
