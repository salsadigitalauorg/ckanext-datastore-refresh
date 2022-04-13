import logging
import requests
import ckan.plugins.toolkit as toolkit
import ckan.lib.formatters as formatters
import ckan.lib.dictization as d
import ckan.lib.helpers as h

import ckanext.datastore_refresh.choices as choices

from ckan.lib.navl.dictization_functions import unflatten
from ckan.logic import clean_dict, tuplize_dict, parse_params
from ckan.views.api import API_DEFAULT_VERSION

from ckanext.datastore_refresh.model import RefreshDatasetDatastore as rdd


log = logging.getLogger(__name__)


def get_frequency_options():
    return choices.load_options()


def clean_params(params):
    return clean_dict(unflatten(tuplize_dict(parse_params(params))))


def get_datastore_refresh_configs():
    return toolkit.get_action('refresh_dataset_datastore_list')({}, {})


def get_datasore_refresh_config_option(frequency):
    options = get_frequency_options()
    res = [option['text'] for option in options if option['value'] == frequency]
    if res:
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


def purge_section_cache(context, resource_dict, dataset_dict):
    try:
        cache_ban_url = toolkit.config.get('ckanext.datastore_refresh.cache_ban_url')
        if cache_ban_url:
            rdd = toolkit.get_action('refresh_datastore_dataset_update')(context, {'package_id': dataset_dict.get('id')})
            if rdd:
                cache_user = toolkit.config.get('ckanext.datastore_refresh.cache_user')
                cache_pass = toolkit.config.get('ckanext.datastore_refresh.cache_pass')
                cache_account_id = toolkit.config.get('ckanext.datastore_refresh.cache_account_id')
                cache_application_id = toolkit.config.get('ckanext.datastore_refresh.cache_application_id')
                cache_environment_id = toolkit.config.get('ckanext.datastore_refresh.cache_environment_id')

                cache_url = f"{cache_ban_url}/account/{cache_account_id}/application/{cache_application_id}/environment/{cache_environment_id}/proxy/varnish/state?banExpression=req.url ~ "
                auth = (cache_user, cache_pass)
                headers = {"Content-Type": "application/json"}

                # There could be two api paths to clear. One with api version and one with out
                api_noversion_endpoint = f"/api/action/datastore_search?id={resource_dict.get('id')}"
                api_default_version_endpoint = f"/api/{API_DEFAULT_VERSION}/action/datastore_search?id={resource_dict.get('id')}"
                api_endpoints = [api_noversion_endpoint, api_default_version_endpoint]

                for api_endpoint in api_endpoints:
                    url = f"{cache_url}{api_endpoint}"
                    # Ping CDN to purge/clear cache
                    response = requests.post(url, auth=auth, headers=headers)
                    if response.ok:
                        log.info(f"Successfully purged cache for api {api_endpoint}")
                    else:
                        log.error(f"Failed to purged cache for api {api_endpoint}: {response.reason}")

    except Exception as ex:
        log.error(ex)
