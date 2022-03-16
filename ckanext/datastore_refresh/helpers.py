import logging
import ckan.plugins.toolkit as toolkit
import ckan.lib.formatters as formatters
import ckan.lib.dictization as d
import ckan.lib.helpers as h

from ckan.lib.navl.dictization_functions import unflatten
from ckan.logic import clean_dict, tuplize_dict, parse_params

from ckanext.datastore_refresh.model import RefreshDatasetDatastore as rdd


log = logging.getLogger(__name__)


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
    if isinstance(datetime, str):
        datetime = h.date_str_to_datetime(datetime)
    # the localised date
    return formatters.localised_nice_date(datetime, show_date=False)


def dictize_two_objects(context, results):
    '''Returns model objects as a dictionary
    :param results: list of model objects: RefreshDatasetDatastore, Package
    :type results: list
    '''
    model = context['model']
    data_dict = dict()
    data_dict['refresh_dataset_datastore'] = list()

    for index, result in enumerate(results):
        for res in result:
            if isinstance(res, rdd):
                data_dict['refresh_dataset_datastore'].append(d.table_dictize(res, {'model': model}))
            else:
                data_dict['refresh_dataset_datastore'][index]['package'] = dict()
                data_dict['refresh_dataset_datastore'][index]['package'] = d.table_dictize(res, {'model': model})
                log.info(toolkit._('Refresh dataset by frequency: {0}').format(res.name))

    return data_dict