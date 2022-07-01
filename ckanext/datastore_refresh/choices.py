import json
import logging

import ckan.plugins.toolkit as toolkit
from ckan.common import config

from .logic.schema import default_frequency_options_schema

log = logging.getLogger(__name__)

DEFAULT_VALUES = [
    {"value": "10", "text": "10 minutes"},
    {"value": "120", "text": "2 hours"},
    {"value": "1440", "text": "Daily"},
]


def load_options():
    frequency_options_path = config.get(
        "ckanext.datastore_refresh.frequency_options"
    )
    if frequency_options_path:
        with open(frequency_options_path) as f:
            content = f.read()
            choices = json.loads(content)

            data, errors = toolkit.navl_validate(
                choices, default_frequency_options_schema()
            )
            if errors:
                raise toolkit.ValidationError(errors)

            try:
                return data["frequency_options"]
            except KeyError as e:
                log.error(f"KeyError: {e} - returning default values...")
                return DEFAULT_VALUES
    return DEFAULT_VALUES
