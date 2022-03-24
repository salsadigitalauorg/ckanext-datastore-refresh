import json

import ckan.plugins.toolkit as toolkit
from ckan.common import config

from ckanext.datastore_refresh.schema import default_frequency_options_schema


DEFAULT_VALUES = [
    {"value": "5", "text": "5 minutes"}, 
    {"value": "120", "text": "2 hours"}, 
    {"value": "1440", "text": "Dialy"}
]

def load_options():
    frequency_options = config.get('ckanext.datastore_refresh.frequency_options')
    if frequency_options:
        with open(frequency_options) as f:
            choices = f.read()
            choices = json.loads(choices)

            data, errors = toolkit.navl_validate(choices, default_frequency_options_schema())
            if errors:
                raise toolkit.ValidationError(errors)
            return data["frequency_options"]
    return DEFAULT_VALUES



