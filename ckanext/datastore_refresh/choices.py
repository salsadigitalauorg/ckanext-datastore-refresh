import json
from ckan.common import config

DEFAULT_VALUES = [
    {"value": "5m", "text": "5 minutes"}, 
    {"value": "2h", "text": "2 hours"}, 
    {"value": "24h", "text": "Dialy"}
]

def load_options():
    frequency_options = config.get('ckanext.datastore_refresh.frequency_options')
    if frequency_options:
        with open(frequency_options) as f:
            choices = f.read()
            choices = json.loads(choices)
            return choices["frequency_options"]
    return DEFAULT_VALUES
