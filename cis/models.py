from typing import Tuple, NewType

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from fernet_fields import EncryptedCharField

from accounts.models import User


CIId = NewType('CIId', int)


class Company(models.Model):
    """Model representing an abstract Company.

    Base for Client, ISP and Manufacturer
    """

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ['name']


class Client(Company):
    """Model representing a Client company"""

    search_fields = ('name',)

    def get_absolute_url(self):
        return reverse('cis:client_detail', args=(self.id,))

    def __str__(self):
        return self.name


class Place(models.Model):
    """Model representing a location of a Client"""

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.client} | {self.name}"

    def get_absolute_url(self):
        return reverse('cis:place_update', args=(self.pk,))

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['client', 'name'],
                name='unique_client_place_name'
            )
        ]


class ISP(Company):
    """Model representing a Internet Service Provider company"""


class Manufacturer(Company):
    """Model representing a Manufacturer of a Configuration Item"""


class Circuit(models.Model):
    """Model representing a Circuit of a ISP installed in a Place"""

    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    isp = models.ForeignKey(ISP, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=50)
    bandwidth = models.CharField(max_length=10)
    type = models.CharField(max_length=50)
    description = models.CharField(max_length=255, help_text="")

    def __str__(self):
        return f"{self.isp.name} | {self.identifier} | {self.bandwidth}"


class Contract(models.Model):
    """Model representing a Contract applied to a CI"""

    name = models.CharField(max_length=100, unique=True)
    begin = models.DateField()
    end = models.DateField()
    description = models.TextField()

    def __str__(self):
        return self.name


class ApplianceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('manufacturer')


class Appliance(models.Model):
    """Model representing a physical or virtual Appliance that compounds a Configuration Item"""

    # modify the initial queryset to join the Manufacturer
    objects = ApplianceManager()

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=255, unique=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True)
    model = models.CharField(max_length=100)
    virtual = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.manufacturer} | {self.model} | {self.serial_number}"

    def get_absolute_url(self):
        return reverse('cis:appliance_update', args=(self.pk,))

    class Meta:
        ordering = ['serial_number']


class Credential(models.Model):
    """Model representing access credentials of a Configuration Item"""

    credential_id = models.AutoField(primary_key=True)
    username = EncryptedCharField(max_length=50)
    password = EncryptedCharField(max_length=50)
    enable_password = EncryptedCharField(max_length=50)
    instructions = EncryptedCharField(max_length=255, blank=True, null=True)


class CIPack(models.Model):
    """
    Model representing a pack of CIs.

    It is used to send CIs to production.
    """

    responsible = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    sent_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='cipacks_approved',
        limit_choices_to={'is_superuser': True}
    )

    @property
    @admin.display(description='Approved (%)')
    def percentage_of_cis_approved(self) -> int:
        num_cis_approved = self.ci_set.filter(status=2).count()
        if not num_cis_approved:
            return 0
        return round((num_cis_approved / len(self)) * 100)

    def send_to_production(self, ci_pks: Tuple[CIId, ...]):
        cis = CI.objects.filter(pk__in=ci_pks)
        self.ci_set.set(cis)
        self.ci_set.update(status=1)

    def approve_all_cis(self):
        self.ci_set.update(status=2)

    def __len__(self):
        return self.ci_set.count()

    def __str__(self):
        local_date = timezone.localtime(self.sent_at)
        return f"{self.responsible} {local_date.strftime('%Y-%m-%d %H:%M:%S')}"


class CI(Credential):
    """
    Model representing a Configuration Item.

    It is composed of a Setup and a Credential.
    https://docs.djangoproject.com/en/stable/topics/db/models/#multiple-inheritance
    """

    IMPACT_OPTIONS = (
        (0, 'low'),
        (1, 'medium'),
        (2, 'high'),
    )
    STATUS_OPTIONS = (
        (0, 'created'),
        (1, 'sent'),
        (2, 'approved'),
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    appliances = models.ManyToManyField(Appliance)
    hostname = models.CharField(max_length=50)
    ip = models.GenericIPAddressField()
    description = models.CharField(max_length=255)
    deployed = models.BooleanField(default=False)
    business_impact = models.PositiveSmallIntegerField(
        choices=IMPACT_OPTIONS,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(2)],
    )
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True)
    status = models.PositiveSmallIntegerField(
        choices=STATUS_OPTIONS,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(2)],
    )
    pack = models.ForeignKey(CIPack, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.place} | {self.hostname} | {self.ip}"

    def get_absolute_url(self):
        return reverse('cis:ci_detail', args=(self.pk,))

    class Meta:
        ordering = ['hostname']
        constraints = [
            models.UniqueConstraint(
                fields=['client', 'hostname', 'ip', 'description'],
                name='unique_client_hostname_ip_description'
            )
        ]
