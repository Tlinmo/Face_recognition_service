class UserError(Exception):
    pass


class ServiceUsernameError(UserError):
    pass


class AuthPasswordError(UserError):
    pass


class AuthFaceError(UserError):
    pass


class UserUpdateError(UserError):
    pass


class ServiceDataBaseError(Exception):
    pass


class EmbeddingVectorSizeError(ValueError):
    pass