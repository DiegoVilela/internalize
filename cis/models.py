from django.db import models


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


class Site(models.Model):
    """Model representing a location of a Client"""

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.client} | {self.name}"


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

    serial_number = models.CharField(max_length=255)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True)
    model = models.CharField(max_length=100)
    virtual = models.BooleanField()

    def __str__(self):
        return f"{self.manufacturer} | {self.model} | {self.serial_number}"


class Setup(models.Model):
    """Model representing a Setup applied to a Configuration Item"""

    hostname = models.CharField(max_length=50)
    ip = models.GenericIPAddressField()
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=100, default='deployed')
    business_impact = models.CharField(max_length=10, default='low')

    def __str__(self):
        return f"{self.hostname} | {self.ip} | {self.description}"


class Credentials(models.Model):
    """Model representing the credentials to log in a Configuration Item"""

    username = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=50, blank=True, null=True)
    enable_password = models.CharField(max_length=50, blank=True, null=True)
    instructions = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.username}"


class CI(models.Model):
    """Model representing a Configuration Item"""

    appliances = models.ManyToManyField(Appliance)
    setup = models.OneToOneField(Setup, on_delete=models.SET_NULL, null=True)
    credentials = models.OneToOneField(Credentials, on_delete=models.SET_NULL, null=True)
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True)
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.site} | {self.setup}"
