import datetime
import uuid

from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID

from common.app_common import db


class ModelAbstract(db.Model):
    __abstract__ = True

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = db.Column(TIMESTAMP, default=datetime.datetime.now())
    updated_at = db.Column(TIMESTAMP, default=datetime.datetime.now())

    def __repr__(self):
        return "<{0.__class__.__name__}>".format(self)
