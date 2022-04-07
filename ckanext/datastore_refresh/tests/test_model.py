import pytest
import datetime
import ckan.tests.helpers as helpers
import ckan.tests.factories as factories

from ckanext.datastore_refresh.model import RefreshDatasetDatastore as rdd, setup


@pytest.fixture
def init_db():
    setup()


@pytest.mark.usefixtures("clean_db", "init_db")
def test_create():
    dataset = factories.Dataset()
    user = factories.Sysadmin()
    results = rdd(dataset_id=dataset["id"], frequency="5", created_user_id=user["id"])
    results.save()
    obj = rdd.get(results.id)

    assert obj.id is not None
    assert obj.dataset_id == dataset["id"]
    assert obj.frequency == "5"
    assert obj.created_user_id == user["id"]
    assert obj.datastore_last_refreshed is None


@pytest.mark.freez_time
@pytest.mark.usefixtures("clean_db", "init_db")
def test_update(freezer):
    dataset = factories.Dataset()
    user = factories.Sysadmin()
    results = rdd(dataset_id=dataset["id"], frequency="5", created_user_id=user["id"])
    results.save()
    obj = rdd.get(results.id)

    assert obj.datastore_last_refreshed is None

    freezer.move_to(datetime.datetime.utcnow())
    helpers.call_action(
        "refresh_datastore_dataset_update",
        context={"auth_user_obj": user},
        package_id=obj.dataset_id,
    )
    assert obj.datastore_last_refreshed == datetime.datetime.utcnow()


@pytest.mark.usefixtures("clean_db", "init_db")
def test_delete():
    dataset = factories.Dataset()
    user = factories.Sysadmin()
    results = rdd(dataset_id=dataset["id"], frequency="5", created_user_id=user["id"])
    results.save()
    obj = rdd.get(results.id)

    assert obj
    rdd.delete(obj.id)
    assert rdd.get(obj.id) is None
