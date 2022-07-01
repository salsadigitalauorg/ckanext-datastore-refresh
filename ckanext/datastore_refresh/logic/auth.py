from __future__ import annotations

from ckan.authz import is_authorized
from ckanext.toolbelt.decorators import Collector

auth, get_auth_functions = Collector("datastore_refresh").split()

@auth
def dataset_refresh_create(context, data_dict):
    return is_authorized("sysadmin", context, data_dict)


@auth
def dataset_refresh_update(context, data_dict):
    return is_authorized("sysadmin", context, data_dict)


@auth
def dataset_refresh_list(context, data_dict):
    return is_authorized("sysadmin", context, data_dict)


@auth
def dataset_refresh_list_by_frequency(context, data_dict):
    return is_authorized("sysadmin", context, data_dict)


@auth
def dataset_refresh_delete(context, data_dict):
    return is_authorized("sysadmin", context, data_dict)
