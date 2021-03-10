class AddClientMixin:
    """
    Add the client to be saved on create views.

    Override form_valid() of CreateView.
    https://docs.djangoproject.com/en/stable/topics/class-based-views/generic-editing/#models-and-request-user
    """
    def form_valid(self, form):
        form.instance.client = self.request.user.client
        return super().form_valid(form)
