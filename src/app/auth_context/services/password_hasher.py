import bcrypt

from dddesign.structure.services import Service


class HashPasswordService(Service):
    password: str

    def handle(self) -> str:
        return bcrypt.hashpw(self.password.encode(), bcrypt.gensalt()).decode()


class VerifyPasswordService(Service):
    password: str
    hashed_password: str

    def handle(self) -> bool:
        return bcrypt.checkpw(self.password.encode(), self.hashed_password.encode())
