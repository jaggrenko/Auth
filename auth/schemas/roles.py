from common.app_common import ma
from db.db_models import Roles, UserRole


class RoleSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Roles
        fields = ('id', 'role', 'description')


class UserRoleSchema(ma.SQLAlchemySchema):
    class Meta:
        model = UserRole
        fields = ('id', 'user_id', 'role_id')


role_schema = RoleSchema()
user_role_schema = UserRoleSchema()
