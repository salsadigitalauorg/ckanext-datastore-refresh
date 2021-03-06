from ckan.model.meta import metadata, mapper, Session, engine
from ckan.model.domain_object import DomainObject
from ckan.model.types import make_uuid
from ckan.model.package import Package
from sqlalchemy import types, Column, Table, ForeignKey, orm, text

import datetime
import logging

log = logging.getLogger(__name__)

refresh_dataset_datastore_table = None


refresh_dataset_datastore_table = Table(
    'refresh_dataset_datastore',
    metadata,
    Column('id',
        types.UnicodeText,
        primary_key=True,
        default=make_uuid()),
    Column('dataset_id',
        types.UnicodeText, ForeignKey('package.id'),
        nullable=False,
        index=True),
    Column('frequency',
        types.UnicodeText,
        nullable=False),
    Column('created_user_id',
        types.UnicodeText, ForeignKey('user.id'),
        nullable=False),
    Column('created_at',
        types.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow),
    Column('datastore_last_refreshed',
        types.DateTime,
        nullable=True)
)

class RefreshDatasetDatastore(DomainObject):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.id = make_uuid()
        self.created_at = datetime.datetime.utcnow()

    @classmethod
    def get(cls, id):
        return Session.query(cls).get(id)

    @classmethod
    def delete(cls, id):
        obj = Session.query(cls).get(id)
        if obj:
            Session.delete(obj)
            Session.commit()

    @classmethod
    def get_all(cls):
        query = Session.query(cls, Package).join(Package).filter(Package.id == cls.dataset_id )
        return query.all()

    def get_by_frequency(frequency):
        query = Session.query(RefreshDatasetDatastore, Package).join(Package).filter(RefreshDatasetDatastore.frequency==frequency)
        return query.all()

    def get_by_package_id(package_id):
        query = Session.query(RefreshDatasetDatastore).filter(RefreshDatasetDatastore.dataset_id==package_id)
        return query.one()


mapper(RefreshDatasetDatastore, refresh_dataset_datastore_table,
properties={
        u"dataset": orm.relationship(
            Package, 
            primaryjoin=refresh_dataset_datastore_table.c.dataset_id == Package.id,
            backref=orm.backref(u"refresh_dataset_datastores",
            cascade=u"all, delete")
        )}
)


def setup():
    if not refresh_dataset_datastore_table.exists():
        refresh_dataset_datastore_table.create()