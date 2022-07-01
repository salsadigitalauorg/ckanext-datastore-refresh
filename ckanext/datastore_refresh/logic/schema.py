from ckan.logic.schema import validator_args


@validator_args
def default_frequency_options_schema(not_empty, unicode_safe):
    return {
        "frequency_options": {
            "value": [not_empty, unicode_safe],
            "text": [not_empty, unicode_safe],
        }
    }
