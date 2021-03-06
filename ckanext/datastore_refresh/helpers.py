import ckan.plugins.toolkit as toolkit
import ckan.lib.formatters as formatters

from ckan.lib.navl.dictization_functions import unflatten
from ckan.logic import clean_dict, tuplize_dict, parse_params


def get_frequency_options():
    return [
        {'value': '10', 'text': '10 minutes'},
        {'value': '2',  'text': '2 hours'},
        {'value': '24', 'text': 'Daily'}]


def clean_params(params):
    return clean_dict(unflatten(tuplize_dict(parse_params(params))))


def get_datastore_refresh_configs():
    return toolkit.get_action('refresh_dataset_datastore_list')({}, {})


def get_datasore_refresh_config_option(frequency):
    options = get_frequency_options()
    res = [option['text'] for option in options if option['value'] == frequency]
    return res[0]


def time_ago_from_datetime(datetime):
    ''' Returns a string like `5 months ago` for a datetime relative to now
    :param timestamp: the timestamp or datetime
    :type timestamp: string or datetime

    :rtype: string
    '''
    if not datetime:
        return None
    # the localised date
    return formatters.localised_nice_date(datetime, show_date=False)

