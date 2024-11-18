class UserError(Exception):
    pass


class AuthUsernameError(UserError):
    pass


class AuthPasswordError(UserError):
    pass


class UserUpdateError(UserError):
    pass


class ServiceDataBaseError(Exception):
    pass
