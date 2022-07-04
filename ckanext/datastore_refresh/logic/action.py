import logging

import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import sqlalchemy
from ckan.logic import validate

from ckanext.datastore_refresh.model import DatasetRefresh as rdd
from ckanext.toolbelt.decorators import Collector
from . import schema

action, get_actions = Collector("datastore_refresh").split()

log = logging.getLogger(__name__)
ValidationError = toolkit.ValidationError


@action
@validate(schema.dataset_refresh_create)
def dataset_refresh_create(context, data_dict):
    """Create a new dataset refresh schedule.

    :param package_id: id of the dataset
    :type package_id: string
    :param frequency: frequency of the refresh
    :type frequency: string

    :returns: the newly created refresh_dataset_datastore

    """
    logic.check_access(
        "datastore_refresh_dataset_refresh_create", context, data_dict
    )

    session = context["session"]
    user = context["auth_user_obj"]
    dataset = toolkit.get_action("package_show")(
        context, {"id": data_dict["package_id"]}
    )

    rdd_obj = rdd(
        dataset_id=dataset["id"],
        frequency=data_dict["frequency"],
        created_user_id=user.id,
    )

    try:
        rdd_obj.save()
    except Exception as e:
        session.rollback()
        log.error("Error creating refresh_dataset_datastore: %s", e)
        raise ValidationError(
            {"package_id": ["Error while creating refresh_dataset_datastore"]}
        )

    return rdd_obj.dictize(context)


@action
@validate(schema.dataset_refresh_update)
def dataset_refresh_update(context, data_dict):
    """Update a dataset refresh schedule.

    :param package_id: id of the dataset
    :type package_id: string

    :returns: none
    """
    logic.check_access("datastore_refresh_dataset_refresh_update", context)

    rdd_obj = rdd.get_by_package_id(data_dict["package_id"])
    if not rdd_obj:
        log.error(
            "Refresh_dataset_datastore not found: %s", data_dict["package_id"]
        )
        return None

    log.debug("Updating refresh_dataset_datastore: %s", rdd_obj)
    rdd_obj.touch()
    rdd_obj.save()

    return rdd_obj.dictize(context)


@action
@toolkit.side_effect_free
def dataset_refresh_list(context, data_dict):
    """List all dataset refresh schedules.

    :returns: a list of all refresh_dataset_datastores
    """
    logic.check_access("datastore_refresh_dataset_refresh_list", context)
    results = results = rdd.get_all()

    return {
        "refresh_dataset_datastore": rdd.dictize_collection(
            results, {"model": model, "dataset_refresh_include_package": True}
        )
    }


@action
@validate(schema.dataset_refresh_list_by_frequency)
def dataset_refresh_list_by_frequency(context, data_dict):
    """List all dataset refresh schedules by frequency.

    :param frequency: frequency of the refresh
    :type frequency: string

    :returns: a list of all refresh_dataset_datastores by frequency

    """
    toolkit.check_access(
        "datastore_refresh_dataset_refresh_list_by_frequency", context
    )

    results = rdd.get_by_frequency(data_dict.get("frequency"))

    return {
        "refresh_dataset_datastore": rdd.dictize_collection(
            results, dict(context, dataset_refresh_include_package=True)
        )
    }


@action
@validate(schema.dataset_refresh_delete)
def dataset_refresh_delete(context, data_dict):
    """Delete a dataset refresh schedule.

    :param id: id of the refresh_dataset_datastore
    :type id: string

    :returns: the deleted refresh_dataset_datastore

    """
    toolkit.check_access("datastore_refresh_dataset_refresh_delete", context)

    rdd_id = data_dict["id"]
    log.info("Deleting refresh_dataset_datastore: %s", rdd_id)
    rdd_obj = rdd.get(rdd_id)

    if not rdd_obj:
        log.error("Refresh_dataset_datastore not found: %s", rdd_id)
        raise ValidationError("Not found")

    rdd.delete(rdd_id)
