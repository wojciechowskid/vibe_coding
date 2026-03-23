from dddesign.structure.domains.constants import BaseEnum


class TokenType(str, BaseEnum):
    ACCESS = 'access'
    REFRESH = 'refresh'
