"""
Field names and their column location (zero-indexed) on the spreadsheet
"""

CIS_SHEET = 'cis'
# Fields in "cis" sheet
HOSTNAME = 0
IP = 1
DESCRIPTION = 2
DEPLOYED = 3
BUSINESS_IMPACT = 4

# Site fields in "cis" sheet
PLACE = 5
PLACE_DESCRIPTION = 6

# Contract fields in "cis" sheet
CONTRACT = 7
CONTRACT_BEGIN = 8
CONTRACT_END = 8
CONTRACT_DESCRIPTION = 10

# Credential fields in "cis" sheet
CREDENTIAL_USERNAME = 11
CREDENTIAL_PASSWORD = 12
CREDENTIAL_ENABLE_PASSWORD = 13
CREDENTIAL_INSTRUCTIONS = 14

# Appliances fields in "appliances" sheet
APPLIANCES_SHEET = 'appliances'
APPLIANCE_HOSTNAME = 0
APPLIANCE_SERIAL_NUMBER = 1
APPLIANCE_MANUFACTURER = 2
APPLIANCE_MODEL = 3
APPLIANCE_VIRTUAL = 4
