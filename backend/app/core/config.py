from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Teaching Framework API"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8081
    app_debug: bool = True
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "edu_user"
    mysql_password: str = "edu_password"
    mysql_db: str = "teaching_framework"
    jwt_secret_key: str = "please-change-this-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cors_allow_origins: str = "*"
    cors_allow_methods: str = "*"
    cors_allow_headers: str = "*"
    cors_allow_credentials: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
            "?charset=utf8mb4"
        )

    @staticmethod
    def _parse_csv_config(value: str) -> list[str]:
        if not value:
            return []
        if value.strip() == "*":
            return ["*"]
        return [item.strip() for item in value.split(",") if item.strip()]

    @property
    def cors_allow_origins_list(self) -> list[str]:
        return self._parse_csv_config(self.cors_allow_origins) or ["*"]

    @property
    def cors_allow_methods_list(self) -> list[str]:
        return self._parse_csv_config(self.cors_allow_methods) or ["*"]

    @property
    def cors_allow_headers_list(self) -> list[str]:
        return self._parse_csv_config(self.cors_allow_headers) or ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
