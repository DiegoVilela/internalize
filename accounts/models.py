from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


class UserClientManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().select_related('client')


class User(AbstractUser):
    client = models.ForeignKey('cis.Client', on_delete=models.CASCADE, blank=True, null=True)

    # modify the user manager's initial QuerySet to join the Client
    # https://docs.djangoproject.com/en/3.1/topics/db/managers/#modifying-a-manager-s-initial-queryset
    objects = UserClientManager()

    def __str__(self):
        return self.email

    @property
    def is_approved(self):
        return bool(self.client) or self.is_superuser
