from __future__ import annotations

import datetime

import ckan.model as model
from ckan.model.types import make_uuid
from sqlalchemy import Column, ForeignKey, UnicodeText, DateTime, orm

from .base import Base

refresh_dataset_datastore_table = None


class RefreshDatasetDatastore(Base):
    __tablename__ = "refresh_dataset_datastore"
    id = Column(UnicodeText, primary_key=True, default=make_uuid)
    dataset_id = Column(
        UnicodeText,
        ForeignKey(model.Package.id),
        nullable=False,
    )
    frequency = Column(UnicodeText, nullable=False)
    created_user_id = Column(
        UnicodeText,
        ForeignKey("user.id"),
        nullable=False,
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
    )
    datastore_last_refreshed = Column(DateTime, nullable=True)

    dataset = orm.relationship(
        model.Package,
        backref=orm.backref(
            "refresh_dataset_datastores", cascade="all, delete-orphan"
        ),
    )

    def save(self):
        model.Session.add(self)
        model.Session.commit()

    @classmethod
    def get(cls, id):
        return model.Session.query(cls).get(id)

    @classmethod
    def delete(cls, id):
        obj = model.Session.query(cls).get(id)
        if obj:
            model.Session.delete(obj)
            model.Session.commit()

    @classmethod
    def get_all(cls):
        query = (
            model.Session.query(cls, model.Package)
            .join(model.Package)
            .filter(model.Package.id == cls.dataset_id)
        )
        return query.all()

    def get_by_frequency(frequency):
        query = (
            model.Session.query(RefreshDatasetDatastore, model.Package)
            .join(model.Package)
            .filter(RefreshDatasetDatastore.frequency == frequency)
        )
        return query.all()

    def get_by_package_id(package_id):
        query = model.Session.query(RefreshDatasetDatastore).filter(
            RefreshDatasetDatastore.dataset_id == package_id
        )
        return query.first()
