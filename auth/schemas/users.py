from common.app_common import ma
from db.db_models import Roles


class UserDataSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Roles


user_data_schema = UserDataSchema()
