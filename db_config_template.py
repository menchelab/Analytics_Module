'''
Database configurations for all DBs used for the DataDivr.

INSTRUCTIONS:
    - Copy this file to ./db_config.py
    - Fill in the database passwords
IMPORTANT: DO NOT put passwords in this file.
'''

# DATABASES

asimov = {  "host":     "asimov.westeurope.cloudapp.azure.com",
            'user':     'readonly',
            'password':  'FILL IN PASSWORD',
            'database': 'Datadivr_tmp',
}

menche = {  "host":     "menchelabdb.int.cemm.at",
            'user':     'readonly',
            'password':  'FILL IN PASSWORD',
            'database': 'Datadivr_tmp',
}


test = {  # TODO, but probably best sqlite3 since that ships with anaconda.

}

# Update this variable to switch db used by the platform
DATABASE = asimov
