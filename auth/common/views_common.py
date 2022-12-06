import uuid
from abc import ABC, abstractmethod
from functools import wraps
from http import HTTPStatus
from typing import Any, AnyStr, Literal

from flask import Response, make_response
from flask.views import MethodView
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from common.app_common import db
from db.db_models import Permissions, RolePermission, UserRole

Status = Literal["success", "error"]


def permission_validate(permission):
    def _permission_validate(f):
        @wraps(f)
        def __permission_validate(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()

            has_permissions = True in [
                kwargs.get('user_id') == uuid.UUID(get_jwt_identity()),
                claims.get('is_superuser'),
                permission in claims.get('permissions', [])]

            if has_permissions:
                return f(*args, **kwargs)

            return make_response(
                {
                    "message": "Permission denied",
                    "status": "error"
                }, HTTPStatus.FORBIDDEN)

        return __permission_validate

    return _permission_validate


class MakeResponseMixin():
    def response(self, message: AnyStr, status: Status,
                 http_status: HTTPStatus.__int__, **kwargs) -> Response:
        return make_response(
            {
                "message": message,
                "status": status,
                **kwargs
            }, http_status)


class FindUserByNameMixin():
    def user_find(self, model: db, unique_object: Any):
        user = model.query.filter_by(name=unique_object).first()

        return user if user else None


class FindUserByIdMixin():
    def user_find(self, model: db, unique_object: Any):
        user = model.query.filter_by(id=unique_object).first()

        return user if user else None


class GetUserPermissionsMixin():
    def get_user_permissions(user_id):
        permissions = db.session.query(
            Permissions
        ).join(
            RolePermission
        ).join(
            UserRole, UserRole.role_id == RolePermission.role_id
        ).filter(
            UserRole.user_id == user_id
        ).all()

        return permissions


class DBAddMixin():
    def db_add(self, db: db, unique_object: Any):
        db.session.add(unique_object)
        db.session.commit()


class AbstractView(ABC):
    pass


class FindRoleByCodeMixin():
    def role_find(self, model: db, unique_object: Any):
        role = model.query.filter_by(code=unique_object).first()

        return role if role else None


class FindRoleByIdMixin():
    def role_find(self, model: db, unique_object: Any):
        role = model.query.filter_by(id=unique_object).first()

        return role if role else None


class UserView(AbstractView, MethodView):

    @property
    def _model(self):
        pass

    @property
    def _name(self):
        pass

    @property
    def _password(self):
        pass

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def post(self):
        pass
