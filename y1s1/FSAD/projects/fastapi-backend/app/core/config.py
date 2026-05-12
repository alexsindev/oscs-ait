# Load environment variables from a .env file
from pydantic import ConfigDict, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_USER: str
    DATABASE_PASS: SecretStr
    DATABASE_HOST: str
    DATABASE_DB: str
    UVICORN_HOST: str
    UVICORN_PORT: int
    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    UPLOAD_DIRECTORY: str
    SEED_DEFAULT_USERS: bool = False

    @property
    def db_url(self) -> str:
        return f"postgresql+psycopg2://{self.DATABASE_USER}:{self.DATABASE_PASS.get_secret_value()}@{self.DATABASE_HOST}/{self.DATABASE_DB}"

    model_config = ConfigDict(env_file=".env")


settings = Settings()
