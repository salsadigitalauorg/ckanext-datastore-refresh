import pytest
import ckan.model as model
from ckan.tests.helpers import call_auth
import ckan.plugins.toolkit as tk


@pytest.mark.parametrize(
    "action", ["create", "update", "list", "list_by_frequency", "delete"]
)
@pytest.mark.usefixtures("with_plugins", "clean_db")
def test_standard_permissions(action, user, sysadmin):
    name = f"datastore_refresh_dataset_refresh_{action}"

    with pytest.raises(tk.NotAuthorized):
        call_auth(name, {"user": ""})

    with pytest.raises(tk.NotAuthorized):
        call_auth(name, {"user": user["name"]})

    call_auth(name, {"user": sysadmin["name"]})
