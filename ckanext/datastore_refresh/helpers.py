from functools import lru_cache
import logging

import ckan.lib.formatters as formatters
import ckan.plugins.toolkit as tk

import ckanext.datastore_refresh.choices as choices
from ckanext.datastore_refresh.model import DatasetRefresh as DatasetRefresh

from ckanext.toolbelt.decorators import Collector

helper, get_helpers = Collector("datastore_refresh").split()

log = logging.getLogger(__name__)


@helper
@lru_cache(1)
def get_frequency_options():
    return choices.load_options()


@helper
def get_datastore_refresh_configs():
    return tk.get_action("datastore_refresh_dataset_refresh_list")({}, {})


@helper
def get_datasore_refresh_config_option(frequency):
    options = tk.h.datastore_refresh_get_frequency_options()
    res = [
        option["text"] for option in options if option["value"] == frequency
    ]
    if res:
        return res[0]


@helper
def time_ago_from_datetime(datetime):
    """Returns a string like `5 months ago` for a datetime relative to now
    :param timestamp: the timestamp or datetime
    :type timestamp: string or datetime

    :rtype: string
    """
    if not datetime:
        return None
    if isinstance(datetime, str):
        datetime = tk.h.date_str_to_datetime(datetime)
    # the localised date
    return formatters.localised_nice_date(datetime, show_date=False)
