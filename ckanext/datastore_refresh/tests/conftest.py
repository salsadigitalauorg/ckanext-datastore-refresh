import pytest
from pytest_factoryboy import register
from ckan.tests import factories


@pytest.fixture
def clean_db(reset_db, migrate_db_for):
    reset_db()
    migrate_db_for("datastore_refresh")


@register
class PackageFactory(factories.Dataset):
    pass


@register
class UserFactory(factories.User):
    pass


register(UserFactory, "sysadmin", sysadmin=True)
