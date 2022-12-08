import uuid
from http import HTTPStatus

from flask import Blueprint, request
from flask.views import MethodView

from common.app_common import db
from common.status_messages import MessageHTTPCommon
from common.views_common import (
    DBAddMixin, FindRoleByCodeMixin,
    FindRoleByIdMixin, MakeResponseMixin,
    permission_validate
)
from core.settings import BluePrintSettings
from db.db_models import Roles, User, UserRole
from schemas.roles import role_schema, user_role_schema


bp_settings = BluePrintSettings()
blueprint = Blueprint(
    "roles", __name__,
    url_prefix='{0}{1}'.format(bp_settings.API_URL, "roles")
)
messages = MessageHTTPCommon()


class RolesList(MethodView, MakeResponseMixin):
    decorators = [permission_validate("roles",)]

    _model = Roles

    def get(self):
        """
        file: ../api_specs/roles/roles_list.yml
        """
        roles = self._model.query.all()

        if roles:
            return self.response(
                messages.role_msg.role_found_msg,
                messages.status_msg.success_msg,
                HTTPStatus.OK,
                **{"roles": [role_schema.dump(role) for
                             role in roles]}
            )
        return self.response(
            messages.role_msg.role_empty_msg,
            messages.status_msg.error_msg,
            HTTPStatus.NO_CONTENT
        )


class RoleCreate(MethodView, MakeResponseMixin, FindRoleByCodeMixin,
                 DBAddMixin):
    decorators = [permission_validate("roles",)]

    _code = "code"
    _description = "description"
    _model = Roles

    def validate(self):
        response = None

        if not self._code or not self._description:
            response = self.response(
                messages.role_msg.role_code_description_empy_msg,
                messages.status_msg.error_msg,
                HTTPStatus.BAD_REQUEST
            )

        if self.role_find(self._model, self._code):
            response = self.response(
                messages.role_msg.role_exists_msg,
                messages.status_msg.error_msg,
                HTTPStatus.BAD_REQUEST
            )

        return response

    def post(self):
        """
        file: ../api_specs/roles/role_create.yml
        """
        self._code = request.json.get(self._code)
        self._description = request.json.get(self._description)

        response = self.validate()

        if not response:
            role = self._model(code=self._code, description=self._description)
            self.db_add(db, role)

            response = self.response(
                messages.role_msg.role_created_msg,
                messages.status_msg.success_msg,
                HTTPStatus.CREATED
            )

        return response


class GetRoleById(MethodView, MakeResponseMixin, FindRoleByIdMixin):
    decorators = [permission_validate("roles",)]

    _model = Roles

    def get(self, role_id):
        """
        file: ../api_specs/roles/role_by_id.yml
        """
        role = self.role_find(self._model, role_id)

        if role:
            return self.response(
                messages.role_msg.role_found_msg,
                messages.status_msg.success_msg,
                HTTPStatus.OK,
                **{"role": role_schema.dump(role)}
            )

        return self.response(
            messages.role_msg.role_found_msg,
            messages.status_msg.error_msg,
            HTTPStatus.NOT_FOUND
        )


class RoleChange(MethodView, MakeResponseMixin, FindRoleByIdMixin, DBAddMixin):
    decorators = [permission_validate("roles",)]

    _model = Roles

    def patch(self, role_id):
        """
        file: ../api_specs/roles/role_change.yml
        """
        role = self.role_find(self._model, role_id)

        if role:
            for key in request.json:
                setattr(role, key, request.json.get(key))
                self.db_add(db, role)

                return self.response(
                    messages.role_msg.role_changed_msg,
                    messages.status_msg.success_msg,
                    HTTPStatus.OK,
                    **{"role": role_schema.dump(role)}
                )

        return self.response(
            messages.role_msg.role_found_msg,
            messages.status_msg.error_msg,
            HTTPStatus.NOT_FOUND
        )


class RoleDelete(MethodView, MakeResponseMixin, FindRoleByIdMixin):
    decorators = [permission_validate("roles",)]

    _model = Roles

    def delete(self, role_id):
        """
        file: ../api_specs/roles/role_delete.yml
        """
        role = self.role_find(role_id)

        if role:
            self._model.query.filter_by(id=role_id).delete()
            db.session.commit()

            return self.response(
                messages.role_msg.role_deleted_msg,
                messages.status_msg.success_msg,
                HTTPStatus.MOVED_PERMANENTLY
            )

        return self.response(
            messages.role_msg.role_not_found_msg,
            messages.status_msg.error_msg,
            HTTPStatus.NOT_FOUND
        )


class RoleAssign(MethodView, MakeResponseMixin):
    decorators = [permission_validate("roles",)]

    _user_id = "user_id"
    _role_id = "role_ids"
    _model = UserRole

    def post(self):
        """
        file: ../api_specs/roles/role_assign.yml
        """
        self._user_id = request.json.get(self._user_id)
        self._role_id = request.json.get(self._role_id)

        roles = [self._model(user_id=self._user_id, role_id=self._role_id)
                 for id in self._role_id]

        db.session.bulk_save_objects(roles)
        db.session.commit()

        self.response(
            messages.role_msg.role_assigned_msg,
            messages.status_msg.success_msg,
            HTTPStatus.CREATED,
            **{"roles": user_role_schema.dump(role) for role in
               roles}
        )


class PermissionsCheck(MethodView, MakeResponseMixin):
    decorators = [permission_validate("roles",)]

    _user_id = "user_id"
    _role_id = "role_ids"

    _model_user = User
    _model_roles = Roles
    _model_user_role = UserRole

    def get_roles(self):
        role = self._model_user_role.query \
            .join(self._model_user) \
            .filter(self._model_user.id.in_([self._user_id])) \
            .join(self._model_roles).filter(self._model_roles.id
                                            .in_(self._role_id)).first()

        return role

    def post(self):
        """
        file: ../api_specs/roles/permissions_check.yml
        """
        self._user_id = uuid.UUID(request.json.get(self._user_id))
        self._role_id = uuid.UUID(request.json.get(self._role_id))

        role = self.get_roles()

        if role:
            return self.response(
                messages.role_msg.role_perms_checked,
                messages.status_msg.success_msg,
                HTTPStatus.OK,
                **{"has_permissions": True}
            )

        return self.response(
            messages.role_msg.role_not_assigned_msg,
            messages.status_msg.error_msg,
            HTTPStatus.NOT_FOUND
        )


blueprint.add_url_rule("/all", view_func=RolesList.as_view("roles_list"))
blueprint.add_url_rule("/create", view_func=RoleCreate.as_view("role_create"))
blueprint.add_url_rule("/<uuid:role_id>",
                       view_func=GetRoleById.as_view("role_find_by_id"))
blueprint.add_url_rule("/<uuid:role_id>",
                       view_func=RoleChange.as_view("role_change"))
blueprint.add_url_rule("/<uuid:role_id>",
                       view_func=RoleDelete.as_view("role_delete"))
blueprint.add_url_rule("/assign", view_func=RoleAssign.as_view("roles_assign"))
blueprint.add_url_rule("/check_perms",
                       view_func=PermissionsCheck.as_view("perms_check"))
