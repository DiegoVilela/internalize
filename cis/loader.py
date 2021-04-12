from collections import namedtuple
from openpyxl import load_workbook
from django.db import IntegrityError, transaction
from .models import Client, Place, CI, Appliance, Place, Contract, Manufacturer
from .cis_mapping import CLIENT_CELL, HOSTNAME, IP, DESCRIPTION, \
    DEPLOYED, BUSINESS_IMPACT, SITE, SITE_DESCRIPTION, CONTRACT, \
    CONTRACT_BEGIN, CONTRACT_END, CONTRACT_DESCRIPTION, CREDENTIAL_USERNAME, \
    CREDENTIAL_PASSWORD, CREDENTIAL_ENABLE_PASSWORD, CREDENTIAL_INSTRUCTIONS, \
    SUMMARY_SHEET, CIS_SHEET, APPLIANCES_SHEET, APPLIANCE_HOSTNAME, APPLIANCE_SERIAL_NUMBER, \
    APPLIANCE_MANUFACTURER, APPLIANCE_MODEL, APPLIANCE_VIRTUAL


class CILoader:
    def __init__(self, file):
        self._workbook = load_workbook(file, read_only=True, data_only=True)
        self.client = self._get_client()
        self.places = {}
        self.contracts = {}
        self.manufacturers = {}
        self.cis = []
        self.errors = []

    def save(self):
        cis_sheet = self._workbook[CIS_SHEET]

        Error = namedtuple('Error', ['exc', 'row'])
        for row in cis_sheet.iter_rows(min_row=2, values_only=True):
            try:
                with transaction.atomic():
                    ci = self._create_ci(row)
                    ci.appliances.set(self._get_ci_appliances(ci, row))
                self.cis.append(ci)
            except IntegrityError as e:
                self.errors.append(Error(e, row))
        return self

    def _create_ci(self, row):
        return CI.objects.create(
            client=self.client,
            hostname=row[HOSTNAME],
            ip=row[IP],
            description=row[DESCRIPTION],
            deployed=bool(row[DEPLOYED]),
            business_impact=self._get_business_impact(row),
            place=self._get_site(row),
            contract=self._get_contract(row),
            username=row[CREDENTIAL_USERNAME],
            password=row[CREDENTIAL_PASSWORD],
            enable_password=row[CREDENTIAL_ENABLE_PASSWORD],
            instructions=row[CREDENTIAL_INSTRUCTIONS],
        )

    def _get_ci_appliances(self, ci, row):
        appliances = set()
        appliances_sheet = self._workbook[APPLIANCES_SHEET]
        for appl_row in appliances_sheet.iter_rows(min_row=2, values_only=True):
            if appl_row[APPLIANCE_HOSTNAME] == row[HOSTNAME]:
                appliances.add(self._get_appliance(appl_row))
        return appliances

    def _get_client(self):
        summary_sheet = self._workbook[SUMMARY_SHEET]
        name = summary_sheet[CLIENT_CELL].value
        self.client, created = Client.objects.get_or_create(name=name)
        return self.client

    def _get_site(self, row):
        if row[SITE] in self.places:
            return self.places[row[SITE]]
        else:
            self.places[row[SITE]], created = Place.objects.get_or_create(
                name=row[SITE],
                description=row[SITE_DESCRIPTION],
                client=self.client
            )
            return self.places[row[SITE]]

    def _get_contract(self, row):
        if row[CONTRACT] in self.contracts:
            return self.contracts[row[CONTRACT]]
        else:
            self.contracts[row[CONTRACT]], created = Contract.objects.get_or_create(
                description=row[CONTRACT_DESCRIPTION],
                name=row[CONTRACT],
                begin=row[CONTRACT_BEGIN],
                end=row[CONTRACT_END],
            )
            return self.contracts[row[CONTRACT]]

    def _get_appliance(self, row):
        appliance, created = Appliance.objects.get_or_create(
            client=self.client,
            serial_number=row[APPLIANCE_SERIAL_NUMBER],
            manufacturer=self._get_manufacturer(row[APPLIANCE_MANUFACTURER]),
            model=row[APPLIANCE_MODEL],
            virtual=bool(str(row[APPLIANCE_VIRTUAL]).strip())
        )
        return appliance

    def _get_manufacturer(self, name):
        if name in self.manufacturers:
            return self.manufacturers[name]
        else:
            self.manufacturers[name], created = Manufacturer.objects.get_or_create(
                name=name,
            )
            return self.manufacturers[name]

    @staticmethod
    def _get_business_impact(row) -> int:
        model_choices = dict(CI.IMPACT_OPTIONS).items()
        options = {value: key for key, value in model_choices}
        return options.get(row[BUSINESS_IMPACT].lower())
