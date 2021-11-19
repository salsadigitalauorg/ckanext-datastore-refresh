import ckan.plugins.toolkit as toolkit
import logging

from ckan.lib.dictization import table_dictize
from ckanext.datastore_refresh.model import RefreshDatasetDatastore

log = logging.getLogger(__name__)
ValidationError = toolkit.ValidationError


def refresh_datastore_dataset_create(context, data_dict):
    """
    Create a new refresh_dataset_datastore

    :param id: id of the refresh_dataset_datastore
    :type id: string
    :param dataset_id: id of the dataset
    :type dataset_id: string
    :param frequency: frequency of the refresh
    :type frequency: string
    :param last_refresh: last refresh
    :type last_refresh: string

    :returns: the newly created refresh_dataset_datastore

    """
    if not data_dict:
        raise ValidationError(toolkit._('No data provided'))

    session = context['session']
    user = context['auth_user_obj']

    rdd = RefreshDatasetDatastore()

    rdd.dataset_id = data_dict.get('dataset_id')
    rdd.frequency = data_dict.get('frequency')
    rdd.created_user_id = user.id

    try:
        rdd.save()
    except Exception as e:
        log.error(toolkit._('Error creating refresh_dataset_datastore: {0}').format(e))
        raise ValidationError(toolkit._('Error while creating refresh_dataset_datastore'))

    session.add(rdd)
    session.commit()

    return table_dictize(rdd, context)


def refresh_dataset_datastore_list(context, data_dict=None):
    """
    List all refresh_dataset_datastores

    :param id: id of the refresh_dataset_datastore
    :type id: string
    
    :returns: a list of all refresh_dataset_datastores
    """

    results = RefreshDatasetDatastore.get_all()
    
    res_dict = []
    log.info(toolkit._('Refresh datastore results: {0}').format(results))
    for res in results:
        
        pkg = res._asdict()
        res_dict.append(pkg)

    return res_dict

def refresh_dataset_datastore_by_frequency(context, data_dict):
    """
    List all refresh_dataset_datastores by frequency

    :param frequency: frequency of the refresh
    :type frequency: string

    :returns: a list of all refresh_dataset_datastores by frequency

    """

    results = RefreshDatasetDatastore.get_by_frequency(data_dict.get('frequency'))
    breakpoint()

    if not results:
        log.info(toolkit._('No refresh_dataset_datastore found for frequency: {0}').format(data_dict.get('frequency')))
        return []

    res_dict = []
    for res in results:
        pkg = res._asdict()
        res_dict.append(pkg)

    return res_dict



def refresh_dataset_datastore_delete(context, data_dict):
    """
    Delete a refresh_dataset_datastore

    :param id: id of the refresh_dataset_datastore
    :type id: string

    :returns: the deleted refresh_dataset_datastore
    
    """

    rdd_id = data_dict['id']

    rdd = RefreshDatasetDatastore.get(rdd_id)

    if rdd:
        log.info(toolkit._('Deleting refresh_dataset_datastore: {0}').format(rdd))
        RefreshDatasetDatastore.delete(rdd_id)
    else:
        log.error(toolkit._('Refresh_dataset_datastore not found: {0}').format(rdd_id))
        raise ValidationError("Not found")
