import ckan.plugins.toolkit as tk
from ckan.logic.schema import validator_args


@validator_args
def default_frequency_options_schema(not_empty, unicode_safe):
    return {
        "frequency_options": {
            "value": [not_empty, unicode_safe],
            "text": [not_empty, unicode_safe],
        }
    }


@validator_args
def dataset_refresh_create(not_missing):
    return {
        "frequency": [not_missing, _validate_frequency_options],
        "package_id": [not_missing],
    }


@validator_args
def dataset_refresh_update(not_missing):
    return {
        "package_id": [not_missing],
    }


@validator_args
def dataset_refresh_delete(not_missing):
    return {
        "id": [not_missing],
    }


@validator_args
def dataset_refresh_list_by_frequency(not_missing):
    return {
        "frequency": [not_missing, _validate_frequency_options],
        # "package_id": [not_missing],
    }


def _validate_frequency_options(value):
    list_of_values = tk.h.get_frequency_options()
    allowed_values = []
    for row in list_of_values:
        if row["value"] != "0":
            allowed_values.append(row["value"])

    if not value or value not in allowed_values:
        raise tk.Invalid("Value must be one of {}".format(allowed_values))
    return value
