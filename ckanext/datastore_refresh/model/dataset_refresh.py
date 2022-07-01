from __future__ import annotations

import datetime
from typing import Optional

from typing_extensions import Self

import ckan.model as model
from ckan.model.types import make_uuid
from sqlalchemy import Column, ForeignKey, UnicodeText, DateTime, orm

from .base import Base

refresh_dataset_datastore_table = None


class DatasetRefresh(Base):
    __tablename__ = "datastore_refresh_dataset_refresh"
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
    def get(cls, id: str) -> Optional[Self]:
        return model.Session.query(cls).get(id)

    @classmethod
    def delete(cls, id):
        obj = model.Session.query(cls).get(id)
        if obj:
            model.Session.delete(obj)
            model.Session.commit()

    @classmethod
    def get_all(cls) -> list[tuple[Self, model.Package]]:
        query = (
            model.Session.query(cls, model.Package)
            .join(model.Package)
            .filter(model.Package.id == cls.dataset_id)
        )
        return query.all()

    @classmethod
    def get_by_frequency(cls, frequency: str) -> list[tuple[Self, model.Package]]:
        query = (
            model.Session.query(cls, model.Package)
            .join(model.Package)
            .filter(cls.frequency == frequency)
        )
        return query.all()

    @classmethod
    def get_by_package_id(cls, package_id: str) -> Optional[Self]:
        query = model.Session.query(cls).filter(
            cls.dataset_id == package_id
        )
        return query.first()
