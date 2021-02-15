from datetime import datetime
from openpyxl import load_workbook
from .models import Client, Site, CI, Appliance, Setup, Credential, Site, Contract, Manufacturer
from .cis_mapping import CLIENT, SETUP_HOSTNAME, SETUP_IP, SETUP_DESCRIPTION, \
    SETUP_STATUS, SETUP_BUSINESS_IMPACT, SITE, SITE_DESCRIPTION, CONTRACT, \
    CONTRACT_BEGIN, CONTRACT_END, CONTRACT_DESCRIPTION, CREDENTIAL_USERNAME, \
    CREDENTIAL_PASSWORD, CREDENTIAL_ENABLE_PASSWORD, CREDENTIAL_INSTRUCTIONS, \
    SUMMARY_SHEET, CIS_SHEET, APPLIANCES_SHEET, APPLIANCE_HOSTNAME, APPLIANCE_SERIAL_NUMBER, \
    APPLIANCE_MANUFACTURER, APPLIANCE_MODEL, APPLIANCE_VIRTUAL


class CILoader:
    def __init__(self, file):
        self._workbook = load_workbook(file, read_only=True, data_only=True)
        self.client = self._get_client()
        self.sites = {}
        self.contracts = {}
        self.manufacturers = {}

    def save(self):
        cis_sheet = self._workbook[CIS_SHEET]
        appliances_sheet = self._workbook[APPLIANCES_SHEET]
        response = FileHandlerResponse(self.client)
        for row in cis_sheet.iter_rows(min_row=2, values_only=True):
            try:
                setup = self._get_setup(row)
                ci = CI.objects.create(
                    setup=setup,
                    site=self._get_site(row),
                    contract=self._get_contract(row),
                    credential=self._get_credential(row)
                )
                for appl_row in appliances_sheet.iter_rows(min_row=2, values_only=True):
                    if appl_row[APPLIANCE_HOSTNAME] == setup.hostname:
                        ci.appliances.add(self._get_appliance(appl_row))

                response.count_ci()
            except Exception as e:
                response.add_error({'exception': e, 'row': row})
        return response

    def _get_client(self):
        summary_sheet = self._workbook[SUMMARY_SHEET]
        name = summary_sheet[CLIENT].value
        self.client, created = Client.objects.get_or_create(name=name)
        return self.client

    def _get_setup(self, row):
        setup = Setup(
            hostname=row[SETUP_HOSTNAME],
            ip=row[SETUP_IP],
            description=row[SETUP_DESCRIPTION],
            status=row[SETUP_STATUS],
            business_impact=row[SETUP_BUSINESS_IMPACT]
        )
        setup.save()
        return setup

    def _get_site(self, row):
        if row[SITE] in self.sites:
            return self.sites[row[SITE]]
        else:
            self.sites[row[SITE]], created = Site.objects.get_or_create(
                name=row[SITE],
                description=row[SITE_DESCRIPTION],
                client=self.client
            )
            return self.sites[row[SITE]]

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

    def _get_credential(self, row):
        credential = Credential(
            username=row[CREDENTIAL_USERNAME],
            password=row[CREDENTIAL_PASSWORD],
            enable_password=row[CREDENTIAL_ENABLE_PASSWORD],
            instructions=row[CREDENTIAL_INSTRUCTIONS]
        )
        credential.save()
        return credential

    def _get_appliance(self, row):
        appliance, created = Appliance.objects.get_or_create(
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


class FileHandlerResponse:

    def __init__(self, client):
        self.client = client
        self.cis_inserted = 0
        self.errors = []

    def add_error(self, exc_dict):
        self.errors.append(exc_dict)

    def count_ci(self):
        self.cis_inserted += 1