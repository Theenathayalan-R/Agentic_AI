from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Metadata API Service"
    TRINO_HOST: str = "starburst-coordinator.your-cluster.com" # Replace with your Starburst host
    TRINO_PORT: int = 8080
    TRINO_USER: str = "your_trino_user"
    TRINO_CATALOG: str = "iceberg" # Your Starburst catalog for Iceberg
    TRINO_SCHEMA: str = "your_iceberg_schema" # Default schema, or specify per request

    # Database for Business Glossary and Feedback
    DB_HOST: str = "your_db_host"
    DB_PORT: int = 5432 # e.g., PostgreSQL default
    DB_USER: str = "your_db_user"
    DB_PASSWORD: str = "your_db_password"
    DB_NAME: str = "metadata_db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()