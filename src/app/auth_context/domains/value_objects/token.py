from dddesign.structure.domains.value_objects import ValueObject


class TokenPair(ValueObject):
    access_token: str
    refresh_token: str
