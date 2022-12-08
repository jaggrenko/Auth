from pydantic import BaseModel, BaseConfig, StrictStr


class MessageHTTPStatus(BaseModel):
    error_msg: StrictStr = "error"
    success_msg: StrictStr = "success"


class RoleMessage(BaseModel):
    role_assigned_msg: StrictStr = "Roles are assigned"
    role_changed_msg: StrictStr = "Role is changed"
    role_code_description_empy_msg: StrictStr = "Code/description is/are empty"
    role_created_msg: StrictStr = "Role created"
    role_deleted_msg: StrictStr = "Role deleted"
    role_empty_msg: StrictStr = "Role is empty"
    role_exists_msg: StrictStr = "Role exists"
    role_found_msg: StrictStr = "Role found"
    role_not_assigned_msg: StrictStr = "Roles are not assigned"
    role_not_found_msg: StrictStr = "Role not found"
    role_perms_checked: StrictStr = "Permissions checked"


class UserMessage(BaseModel):
    user_fields_empty_msg: StrictStr = "Username or/and password is/are empty"
    user_found_msg: StrictStr = "User found"
    user_logout_success_msg: StrictStr = "Logout successful"
    user_name_in_use_msg: StrictStr = "The name is already in use"
    user_not_found_msg: StrictStr = "User not found"
    user_or_pass_not_valid_msg: StrictStr = "Username/password is/are not valid"
    user_registred_success_msg: StrictStr = "New user registered successfully"


class MessageHTTPCommon(BaseConfig):

    jwt_pair_gen_success_msg: StrictStr = "JWT pair generated successfully"
    pass_changed_success_msg: StrictStr = "Password is changed"

    status_msg: MessageHTTPStatus = MessageHTTPStatus()
    role_msg: RoleMessage = RoleMessage()
    user_msg: UserMessage = UserMessage()
