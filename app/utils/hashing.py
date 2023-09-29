from passlib.context import CryptContext

class HashPassword:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_hash_password(self, password):
        return self.pwd_context.hash(password)

    def verify_hash_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)
