"""rename table refresh_dataset_datastore to datastore_refresh_dataset

Revision ID: 638b9fafad7d
Revises: 2cda5f1bc8d4
Create Date: 2022-07-02 00:23:49.844514

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '638b9fafad7d'
down_revision = '2cda5f1bc8d4'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("refresh_dataset_datastore", "datastore_refresh_dataset_refresh")


def downgrade():
    op.rename_table("datastore_refresh_dataset_refresh", "refresh_dataset_datastore")
