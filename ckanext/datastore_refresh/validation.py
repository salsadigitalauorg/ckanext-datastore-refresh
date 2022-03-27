import ckan.plugins.toolkit as toolkit


def validate_frequency_options(value, list_of_values):
    _list_of_values = []
    for row in list_of_values:
        _list_of_values.append(row["value"])

    if not value or value not in _list_of_values:
        raise toolkit.Invalid("Value must be one of {}".format(_list_of_values))
    return value
