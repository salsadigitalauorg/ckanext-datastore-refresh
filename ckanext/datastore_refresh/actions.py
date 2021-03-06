import ckan.plugins.toolkit as toolkit
import logging
import datetime

from ckan.lib.dictization import table_dictize
from ckanext.datastore_refresh.model import RefreshDatasetDatastore as rdd

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

    rdd_obj = rdd()

    rdd_obj.dataset_id = data_dict.get('dataset_id')
    rdd_obj.frequency = data_dict.get('frequency')
    rdd_obj.created_user_id = user.id

    try:
        rdd_obj.save()
    except Exception as e:
        log.error(toolkit._('Error creating refresh_dataset_datastore: {0}').format(e))
        raise ValidationError(toolkit._('Error while creating refresh_dataset_datastore'))

    session.add(rdd_obj)
    session.commit()

    return table_dictize(rdd_obj, context)

def refresh_datastore_dataset_update(context, data_dict):
    """
    Update a refresh_dataset_datastore configuration
    :package 

    :returns: none
    """
    rdd_obj = rdd.get_by_package_id(data_dict['package_id'])
    if not rdd_obj:
        log.error(toolkit._('Refresh_dataset_datastore not found: {0}').format(data_dict['package_id']))
    
    log.info(toolkit._('Updating refresh_dataset_datastore: {0}').format(rdd_obj))
    rdd_obj.datastore_last_refreshed = datetime.datetime.utcnow()
    rdd_obj.save()



def refresh_dataset_datastore_list(context, data_dict=None):
    """
    List all refresh_dataset_datastores

    :param id: id of the refresh_dataset_datastore
    :type id: string
    
    :returns: a list of all refresh_dataset_datastores
    """

    results = rdd.get_all()
    
    res_dict = []
    log.info(toolkit._('Refresh datastore results: {0}').format(results))
    for res in results:
        
        pkg = res._asdict()
        
        log.info(toolkit._('Dataset set for refreshing: {0}').format(pkg))
        res_dict.append(pkg)

    return res_dict

def refresh_dataset_datastore_by_frequency(context, data_dict):
    """
    List all refresh_dataset_datastores by frequency

    :param frequency: frequency of the refresh
    :type frequency: string

    :returns: a list of all refresh_dataset_datastores by frequency

    """
    log.info(toolkit._('Refresh_dataset_datastore by frequency: {0}').format(data_dict))
    results = rdd.get_by_frequency(data_dict.get('frequency'))

    if not results:
        log.info(toolkit._('No refresh_dataset_datastore found for frequency: {0}').format(data_dict.get('frequency')))
        return []

    res_dict = []
    for res in results:
        log.info(toolkit._('Refresh dataset by frequency: {0}').format(res.Package.name))
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
    log.info(toolkit._('Deleting refresh_dataset_datastore: {0}').format(rdd_id))
    rdd_obj = rdd.get(rdd_id)

    if rdd_obj:
        rdd.delete(rdd_id)
    else:
        log.error(toolkit._('Refresh_dataset_datastore not found: {0}').format(rdd_id))
        raise ValidationError("Not found")
