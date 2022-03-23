import ckan.tests.factories as factories
import ckan.tests.helpers as helpers
import ckan.logic as logic
import ckan.model as model
import pytest

from ckan.plugins.toolkit import Invalid

from ckanext.datastore_refresh.actions import ValidationError
from ckanext.datastore_refresh.model import setup


@pytest.fixture
def init_db():
    setup()


@pytest.mark.usefixtures("clean_db", "init_db")
class TestRefreshDatastoreDatasetCreate(object):
    frequency = "5m"

    def create_test_data(self):
        dataset = factories.Dataset()
        sysadmin = factories.Sysadmin()
        sysadmin_obj = model.User.by_name(sysadmin["name"])

        return dataset, sysadmin_obj

    def test_refresh_datastore_dataset_create(self):
        dataset, sysadmin_obj = self.create_test_data()
        data_dict = {"dataset_id": dataset["id"], "frequency": self.frequency}

        results = helpers.call_action(
            "refresh_datastore_dataset_create",
            context={"auth_user_obj": sysadmin_obj},
            **data_dict
        )
        assert dataset["id"] in results["dataset_id"]
        assert self.frequency in results["frequency"]
        assert sysadmin_obj.id in results["created_user_id"]
        assert results["datastore_last_refreshed"] is None

    def test_refresh_datastore_dataset_create_no_frequency(self):
        dataset, sysadmin_obj = self.create_test_data()
        data_dict = {"dataset_id": dataset["id"], "frequency": ""}

        with pytest.raises(ValidationError):
            helpers.call_action(
                "refresh_datastore_dataset_create",
                context={"auth_user_obj": sysadmin_obj},
                **data_dict
            )

    def test_refresh_datastore_dataset_create_no_dataset_id(self):
        _, sysadmin_obj = self.create_test_data()
        data_dict = {"frequency": self.frequency}

        with pytest.raises(ValidationError):
            helpers.call_action(
                "refresh_datastore_dataset_create",
                context={"auth_user_obj": sysadmin_obj},
                **data_dict
            )

    def test_refresh_datastore_dataset_create_fake_dataset_id(self):
        _, sysadmin_obj = self.create_test_data()
        data_dict = {"dataset_id": "fakeid", "frequency": self.frequency}

        with pytest.raises(logic.NotFound):
            helpers.call_action(
                "refresh_datastore_dataset_create",
                context={"auth_user_obj": sysadmin_obj},
                **data_dict
            )

    def test_refresh_datastore_dataset_create_empty_data_dict(self):
        _, sysadmin_obj = self.create_test_data()

        with pytest.raises(ValidationError):
            helpers.call_action(
                "refresh_datastore_dataset_create",
                context={"auth_user_obj": sysadmin_obj},
                data_dict={},
            )

    def test_refresh_datastore_dataset_create_wrong_frequency(self):
        dataset, sysadmin_obj = self.create_test_data()
        data_dict = {"dataset_id": dataset["id"], "frequency": "5"}

        with pytest.raises(Invalid):
            helpers.call_action(
                "refresh_datastore_dataset_create",
                context={"auth_user_obj": sysadmin_obj},
                **data_dict,
            )

    def test_refresh_datastore_dataset_create_anonymous(self):
        dataset, _ = self.create_test_data()
        data_dict = {"dataset_id": dataset["id"], "frequency": "5m"}

        with pytest.raises(logic.NotAuthorized):
            helpers.call_action(
                "refresh_datastore_dataset_create",
                context={"auth_user_obj": "anonymous", "ignore_auth": False},
                **data_dict,
            )

    def test_refresh_datastore_dataset_create_normal_user(self):
        dataset, _ = self.create_test_data()
        data_dict = {"dataset_id": dataset["id"], "frequency": "5m"}
        normal_user = factories.User()
        normal_user_obj = model.User.by_name(normal_user["name"])

        with pytest.raises(logic.NotAuthorized):
            helpers.call_action(
                "refresh_datastore_dataset_create",
                context={"auth_user_obj": normal_user_obj, "ignore_auth": False},
                **data_dict,
            )