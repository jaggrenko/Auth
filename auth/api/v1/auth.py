from http import HTTPStatus

from flask import Blueprint, request
from flask.views import MethodView
from flask_jwt_extended import create_access_token, create_refresh_token, \
    get_jwt, get_jwt_identity, \
    jwt_required
from flask_jwt_extended.exceptions import UserLookupError

from common.app_common import db
from common.views_common import DBAddMixin, FindUserByIdMixin, \
    FindUserByNameMixin, GetUserPermissionsMixin, \
    MakeResponseMixin, UserView, permission_validate
from db.db_models import User


blueprint = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


class Register(UserView, MakeResponseMixin, FindUserByNameMixin, DBAddMixin):

    _name = "name"
    _password = "password"
    _model = User

    def validate(self):
        if not self._name or not self._password:
            return self.response(
                "Fields username or/and password is/are empty",
                "error",
                HTTPStatus.BAD_REQUEST
            )

        if self.user_find(self._model, self._name):
            return self.response(
                "The name is already in use",
                "error",
                HTTPStatus.BAD_REQUEST
            )

        return None

    def post(self):
        """
        file: ../api_specs/auth/register.yml
        """

        print(self._name, self._password)
        self._name = request.json.get(self._name)
        self._password = request.json.get(self._password)

        print(self._name, self._password)

        response = self.validate()

        if not response:
            user = self._model(name=self._name, password=self._password)
            self.db_add(db, user)

            response = self.response("New user was registered successfully",
                                     "success",
                                     HTTPStatus.OK)
        return response


class Login(UserView, MakeResponseMixin, FindUserByNameMixin):
    _name = "username"
    _password = "password"
    _model = User

    def get_tokens(self, user_id):
        # additional_claims = {
        #     self._permissions: permissions,
        #     self._is_superuser: False,
        # }

        access_token = create_access_token(identity=user_id)#, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=user_id)#, additional_claims=additional_claims)

        return access_token, refresh_token

    def validate(self):
        if not self._name or not self._password:
            return self.response(
                "Fields username or/and password is/are empty",
                "error",
                HTTPStatus.BAD_REQUEST
            ), None

        user = self.user_find(self._model, self._name)

        if not user:
            return self.response(
                "User name not found",
                "error",
                HTTPStatus.BAD_REQUEST
            ), None

        if not user.password_validate(self._password):
            return self.response(
                "User name/password is incorrect",
                "error",
                HTTPStatus.UNAUTHORIZED
            ), None

        return None, user

    def post(self):
        """
        file: ../api_specs/auth/login.yml
        """

        self._name = request.json.get(self._name)
        self._password = request.json.get(self._password)

        print(self._name, self._password)

        response, user = self.validate()

        if not response:
            access_token, refresh_token = self.get_tokens(user.id)
            response = self.response(
                "JWT tokens generated successfully",
                "success",
                HTTPStatus.OK,
                **{"tokens": {
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }}
            )

        return response


class Logout(MethodView, MakeResponseMixin):
    decorators = [jwt_required]

    def post(self):
        """
        file: ../api_specs/auth/logout.yml
        """
        response = self.response(
            "logout successful",
            "success",
            HTTPStatus.OK
        )

        return response


class TokenRefresh(MethodView, MakeResponseMixin, GetUserPermissionsMixin,
                   FindUserByIdMixin):
    decorators = [jwt_required(refresh=True)]

    _model = User
    _permissions = "permissions"
    _is_superuser = "is_superuser"

    def get_tokens(self, user_token):
        if user_token:
            permissions, is_superuser = user_token.get(self._permissions, []), \
                                        user_token.get(self._is_superuser,
                                                       False)
        else:
            user = self.user_find(self._model, self._user_id)
            if not user:
                raise UserLookupError("User with ID not found!", self._user_id)

            permissions = [permission.code for permission in
                           self.get_user_permissions(user.id)]
            is_superuser = user.is_superuser

        additional_claims = {
            self._permissions: permissions,
            self._is_superuser: is_superuser,
        }

        access_token = create_access_token(identity=self._user_id,
                                           additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=self._user_id,
                                             additional_claims=additional_claims)

        return access_token, refresh_token

    def post(self):
        """
        file: ../api_specs/auth/token_refresh.yml
        """
        self._user_id, user_token = get_jwt_identity(), get_jwt()

        try:
            access_token, refresh_token = self.get_tokens(self._user_id,
                                                          user_token)
        except UserLookupError:
            return self.response("User not found", "error",
                                 HTTPStatus.UNAUTHORIZED)

        return self.response(
            "JWT pair generation - success",
            "success",
            HTTPStatus.OK,
            **{"tokens":
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            }
        )


class PasswordChange(MethodView, MakeResponseMixin, FindUserByIdMixin, DBAddMixin):
    decorators = [permission_validate("users")]

    _password_old = "old_password"
    _password_new = "new_password"
    _model = User

    def validate(self):
        user = self.user_find(self._model, self._user_id)

        if not user:
            return self.response("User not found!", "error",
                                 HTTPStatus.NOT_FOUND), None

        if not user.password_validate(self._password_old):
            return self.response("Username/password is/are not valid", "error",
                                 HTTPStatus.UNAUTHORIZED), None

        return None, user


    def patch(self, user_id):
        """
        file: ../api_specs/auth/password_change.yml
        """

        self._user_id = user_id

        self._password_old = request.json.get(self._password_old)
        self._password_new = request.json.get(self._password_new)

        response, user = self.validate()

        if user:
            user.password = self._password_new
            self.db_add(db, user)

            return self.response("Password change - success",
                                 "success",
                                 HTTPStatus.OK)

        return response


class GetUserHistory(MethodView, FindUserByIdMixin, MakeResponseMixin):
    decorators = [permission_validate("history")]

    def get(self, user_id):
        """
        file: ../api_specs/auth/user_history.yml
        """
        pass


blueprint.add_url_rule("/register", view_func=Register.as_view("register"))
blueprint.add_url_rule("/login", view_func=Login.as_view("login"))
blueprint.add_url_rule("/logout", view_func=Logout.as_view("logout"))
blueprint.add_url_rule("/token_refresh",
                       view_func=TokenRefresh.as_view("token_refresh"))
blueprint.add_url_rule("/<uuid:user_id>",
                       view_func=PasswordChange.as_view("password_change"))
blueprint.add_url_rule("/<uuid:user_id>",
                       view_func=GetUserHistory.as_view("user_history"))
