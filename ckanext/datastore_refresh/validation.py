import ckan.plugins.toolkit as toolkit


def validate_frequency_options(value, list_of_values):
    allowed_values = []
    for row in list_of_values:
        if row["value"] != "0":
            allowed_values.append(row["value"])

    if not value or value not in allowed_values:
        raise toolkit.Invalid("Value must be one of {}".format(allowed_values))
    return value
