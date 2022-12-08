import os
from datetime import timedelta

from pydantic import (
    BaseConfig, BaseSettings, Field,
    SecretStr, StrictStr, validator
)

SWAGGER_CONFIG = {
    "headers": [
    ],
    "openapi": "3.0.2",
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/openapi/",
    "url_prefix": "/api",
}


class CommonConfig(BaseConfig):
    class Config():
        env_file = "env/auth/.env"


class BluePrintSettings(BaseSettings, CommonConfig):
    PROJECT_NAME: StrictStr = Field(..., env="PROJECT_NAME")
    API_URL: StrictStr = Field(..., env="API_URL")


class JWTSettings(BaseSettings, CommonConfig):
    JWT_SECRET_KEY: StrictStr = Field("super-secret", env="JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = Field(1,
                                                env="JWT_ACCESS_TOKEN_EXPIRES")
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = Field(2,
                                                 env="JWT_REFRESH_TOKEN_EXPIRES")
    JWT_ERROR_MESSAGE_KEY: StrictStr = Field("message",
                                             env="JWT_ERROR_MESSAGE_KEY")


class PostgresDSN(BaseSettings, CommonConfig):
    HOST: StrictStr = Field(..., env="POSTGRES_HOST")
    DB: StrictStr = Field(..., env="POSTGRES_DB")
    PORT: StrictStr = Field(..., env="POSTGRES_PORT")
    PASSWORD: SecretStr = Field(..., env="POSTGRES_PASSWORD")
    USER: StrictStr = Field(..., env="POSTGRES_USER")


class PostgresSettings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: StrictStr = ""
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = True

    @validator("SQLALCHEMY_DATABASE_URI")
    def validate(cls, uri):
        pg: PostgresDSN = PostgresDSN()

        uri = f"postgresql+psycopg2://{pg.USER}:{pg.PASSWORD.get_secret_value()}" \
              f"@{pg.HOST}:{pg.PORT}/{pg.DB}"
        return uri


class RedisDSN(BaseSettings, CommonConfig):
    REDIS_HOST: StrictStr = Field("127.0.0.1", env="REDIS_HOST")
    REDIS_PORT: StrictStr = Field(6389, env="REDIS_PORT")


class RedisSettings(BaseSettings):
    REDIS_URI: StrictStr = ""

    @validator("REDIS_URI")
    def validate(cls, uri):
        rd: RedisDSN = RedisDSN()

        uri = f"redis://{rd.REDIS_HOST}:{rd.REDIS_PORT}"
        return uri


class FlaskSettings(BaseSettings, CommonConfig):
    FLASK_HOST: StrictStr = Field("127.0.0.1", env=("FLASK_HOST"))
    FLASK_PORT: StrictStr = Field(5000, env="FLASK_PORT")
