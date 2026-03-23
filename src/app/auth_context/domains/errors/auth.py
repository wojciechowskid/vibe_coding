from dddesign.structure.domains.errors import BaseError


class UserAlreadyExistsError(BaseError):
    status_code: int = 400
    message: str = 'User with this email already exists'


class InvalidCredentialsError(BaseError):
    status_code: int = 401
    message: str = 'Invalid email or password'


class InvalidTokenError(BaseError):
    status_code: int = 401
    message: str = 'Invalid or expired token'


class InvalidTokenTypeError(BaseError):
    status_code: int = 401
    message: str = 'Invalid token type'
