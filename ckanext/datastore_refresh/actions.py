import datetime
import logging

import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import sqlalchemy
from ckan.lib.dictization import table_dictize

from ckanext.datastore_refresh.helpers import (
    dictize_two_objects,
    get_frequency_options,
)
from ckanext.datastore_refresh.model import RefreshDatasetDatastore as rdd
from ckanext.datastore_refresh.validation import validate_frequency_options

log = logging.getLogger(__name__)
ValidationError = toolkit.ValidationError


def refresh_datastore_dataset_create(context, data_dict):
    """
    Create a new refresh_dataset_datastore

    :param package_id: id of the dataset
    :type package_id: string
    :param frequency: frequency of the refresh
    :type frequency: string

    :returns: the newly created refresh_dataset_datastore

    """
    if not data_dict:
        raise ValidationError(toolkit._("No data provided"))

    if not data_dict.get("frequency"):
        raise ValidationError(toolkit._("No frequency provided"))

    valid_options = get_frequency_options()
    validate_frequency_options(data_dict.get("frequency"), valid_options)

    if not data_dict.get("package_id"):
        raise ValidationError(toolkit._("No dataset_id provided"))

    logic.check_access("refresh_datastore_dataset_create", context, data_dict)

    session = context["session"]
    user = context["auth_user_obj"]
    dataset_id = data_dict.get("package_id")
    dataset = toolkit.get_action("package_show")(context, {"id": dataset_id})

    rdd_obj = rdd()

    rdd_obj.dataset_id = dataset["id"]
    rdd_obj.frequency = data_dict.get("frequency")
    rdd_obj.created_user_id = user.id

    try:
        session.add(rdd_obj)
        session.commit()
    except Exception as e:
        session.rollback()
        log.error(
            toolkit._("Error creating refresh_dataset_datastore: {0}").format(
                e
            )
        )
        raise ValidationError(
            toolkit._("Error while creating refresh_dataset_datastore")
        )

    return table_dictize(rdd_obj, context)


def refresh_datastore_dataset_update(context, data_dict):
    """
    Update a refresh_dataset_datastore configuration
    :package

    :param package_id: id of the dataset
    :type package_id: string

    :returns: none
    """
    session = context["session"]
    if not data_dict.get("package_id"):
        raise ValidationError(toolkit._("No dataset_id provided"))

    logic.check_access("refresh_datastore_dataset_update", context)

    rdd_obj = rdd.get_by_package_id(data_dict["package_id"])
    if not rdd_obj:
        log.error(
            toolkit._("Refresh_dataset_datastore not found: {0}").format(
                data_dict["package_id"]
            )
        )
        return None

    log.info(
        toolkit._("Updating refresh_dataset_datastore: {0}").format(rdd_obj)
    )
    rdd_obj.datastore_last_refreshed = datetime.datetime.utcnow()

    session.add(rdd_obj)
    session.commit()

    return table_dictize(rdd_obj, context)


@toolkit.side_effect_free
def refresh_dataset_datastore_list(context, data_dict=None):
    """
    List all refresh_dataset_datastores

    :returns: a list of all refresh_dataset_datastores
    """
    logic.check_access("refresh_dataset_datastore_list", context)
    results = list()
    try:
        results = rdd.get_all()
    except (
        sqlalchemy.exc.InternalError,
        sqlalchemy.exc.ProgrammingError,
    ) as e:
        log.error(e)

    res_dict = dict()
    if results:
        res_dict = dictize_two_objects({"model": model}, results)

    return res_dict


def refresh_dataset_datastore_by_frequency(context, data_dict):
    """
    List all refresh_dataset_datastores by frequency

    :param frequency: frequency of the refresh
    :type frequency: string

    :returns: a list of all refresh_dataset_datastores by frequency

    """
    if not data_dict.get("frequency"):
        raise ValidationError(toolkit._("No frequency provided"))

    valid_options = get_frequency_options()
    validate_frequency_options(data_dict.get("frequency"), valid_options)

    toolkit.check_access("refresh_dataset_datastore_by_frequency", context)

    log.info(
        toolkit._("Refresh_dataset_datastore by frequency: {0}").format(
            data_dict
        )
    )
    results = rdd.get_by_frequency(data_dict.get("frequency"))

    if not results:
        log.info(
            toolkit._(
                "No refresh_dataset_datastore found for frequency: {0}"
            ).format(data_dict.get("frequency"))
        )
        return []

    data_dict = dictize_two_objects(context, results)
    return data_dict


def refresh_dataset_datastore_delete(context, data_dict):
    """
    Delete a refresh_dataset_datastore

    :param id: id of the refresh_dataset_datastore
    :type id: string

    :returns: the deleted refresh_dataset_datastore

    """
    toolkit.check_access("refresh_dataset_datastore_delete", context)

    rdd_id = data_dict["id"]
    log.info(
        toolkit._("Deleting refresh_dataset_datastore: {0}").format(rdd_id)
    )
    rdd_obj = rdd.get(rdd_id)

    if rdd_obj:
        rdd.delete(rdd_id)
    else:
        log.error(
            toolkit._("Refresh_dataset_datastore not found: {0}").format(
                rdd_id
            )
        )
        raise ValidationError("Not found")
