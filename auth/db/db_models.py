from sqlalchemy.dialects.postgresql import BOOLEAN, TEXT, UUID, VARCHAR
from sqlalchemy.ext.hybrid import hybrid_property

from common.app_common import db
from db.model_abstract import ModelAbstract
from werkzeug.security import check_password_hash, generate_password_hash


class User(ModelAbstract):
    __tablename__ = 'users'

    login = db.Column(VARCHAR(255), unique=True, nullable=True)
    name = db.Column(VARCHAR(255), unique=True, nullable=False)
    email = db.Column(VARCHAR(128), unique=True, nullable=True)
    password_hashed = db.Column(VARCHAR(255), unique=True, nullable=False)
    is_superuser = db.Column(BOOLEAN, default=False)

    @hybrid_property
    def password(self):
        return self.password_hashed

    @password.setter
    def password(self, raw):
        self.password_hashed = generate_password_hash(raw)

    def password_validate(self, raw):
        return check_password_hash(self.password_hashed, raw)

    def __repr__(self):
        return '{}'.format(self.name)


class Roles(ModelAbstract):
    __tablename__ = 'roles'

    role = db.Column(VARCHAR(120), nullable=False, unique=True)
    description = db.Column(TEXT, default='')

    def __repr__(self):
        return '{} {}'.format(self.role, self.description)


class Permissions(ModelAbstract):
    __tablename__ = "permissions"

    code = db.Column(db.VARCHAR(255), nullable=False, unique=True)
    description = db.Column(TEXT, default='')

    def __repr__(self):
        return f'({self.code}) {self.description}'


class UserRole(ModelAbstract):
    __tablename__ = "user_role"

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)


class RolePermission(ModelAbstract):
    __tablename__ = "role_permission"

    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id = db.Column(UUID(as_uuid=True), db.ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)


class History(ModelAbstract):
    __tablename__ = "history"

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    client = db.Column(VARCHAR(120), nullable=False, unique=True)
