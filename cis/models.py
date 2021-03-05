from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    client = models.OneToOneField('Client', on_delete=models.CASCADE, blank=True, null=True)

    @property
    def is_approved(self):
        return self.client or self.is_superuser


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

    def get_absolute_url(self):
        return reverse('cis:client_detail', args=[self.id])

    def __str__(self):
        return self.name


class Site(models.Model):
    """Model representing a location of a Client"""

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.client} | {self.name}"

    def get_absolute_url(self):
        return reverse('cis:site_update', args=[self.pk])


class ISP(Company):
    """Model representing a Internet Service Provider company"""


class Manufacturer(Company):
    """Model representing a Manufacturer of a Configuration Item"""


class Circuit(models.Model):
    """Model representing a Circuit of a ISP installed in a Site"""

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    isp = models.ForeignKey(ISP, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=50)
    bandwidth = models.CharField(max_length=10)
    type = models.CharField(max_length=50)
    description = models.CharField(max_length=255, help_text="")

    def __str__(self):
        return f"{self.isp.name} | {self.identifier} | {self.bandwidth}"


class Contract(models.Model):
    """Model representing a Contract applied to a CI"""

    name = models.CharField(max_length=100)
    begin = models.DateField()
    end = models.DateField()
    description = models.TextField()

    def __str__(self):
        return self.name


class Appliance(models.Model):
    """Model representing a physical or virtual Appliance that compounds a Configuration Item"""

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=255, unique=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True)
    model = models.CharField(max_length=100)
    virtual = models.BooleanField()

    def __str__(self):
        return f"{self.manufacturer} | {self.model} | {self.serial_number}"

    def get_absolute_url(self):
        return reverse('cis:appliance_update', args=[self.pk])


class Credential(models.Model):
    """Model representing access credentials of a Configuration Item's setup"""

    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    enable_password = models.CharField(max_length=50)
    instructions = models.CharField(max_length=255, blank=True, null=True)


class Setup(Credential):
    """
    Model representing a setup of a Configuration Item.

    An example of multi-table-inheritance.
    https://docs.djangoproject.com/en/3.2/topics/db/models/#multi-table-inheritance
    """

    hostname = models.CharField(max_length=50)
    ip = models.GenericIPAddressField()
    description = models.CharField(max_length=255)
    deployed = models.BooleanField(default=False)
    business_impact = models.CharField(max_length=10, default='low')


class CI(Setup):
    """
    Model representing a Configuration Item.

    It is composed of a Setup, which in its turn is composed of a Credential.
    """

    STATUS_OPTIONS = (
        (0, 'CREATED'),
        (1, 'SENT'),
        (2, 'APPROVED'),
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    appliances = models.ManyToManyField(Appliance)
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_OPTIONS, default=0)

    def __str__(self):
        return f"{self.site} | {self.hostname} | {self.ip}"

    def get_absolute_url(self):
        return reverse('cis:ci_detail', args=[self.pk])

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=['client', 'setup'],
    #             name='unique_client_hostname_ip_description'
    #         )
    #     ]


class CIPack(models.Model):
    """Model representing a pack of CIs

    It is used to send CIs to production
    """

    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    sent_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    items = models.ManyToManyField(CI)
    approved = models.BooleanField(default=False)

    def send(self):
        for ci in self.items.all():
            ci.status = 1
            ci.save()

    def __str__(self):
        return f"{self.responsible.client} | {self.responsible} | {self.sent_at}"
