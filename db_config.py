'''
Database configurations for all DBs used for the DataDivr.

INSTRUCTIONS:
    - Copy this file to ./db_config.py
    - Fill in the database passwords
IMPORTANT: DO NOT put passwords in this file.
'''

# DATABASES

vrnetzer = {  "host":     "vrnetzer.westeurope.cloudapp.azure.com",
            'user':     'readonly',
            'password':  'ra4Roh7ohdee',
            'database': 'Vrnetzer'

}


# Update this variable to switch db used by the platform
DATABASE = vrnetzer