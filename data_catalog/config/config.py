from pydantic_settings import BaseSettings

class AiSettings(BaseSettings):
    """
    Configuration settings for AI services.
    The gemini_api_key is set directly here to ensure it's always loaded.
    """
    gemini_api_key: str = "AIzaSyBF9WHShOcTkC4EYQEk5fz25KEHBC7bEl0"
    model_name: str = "gemini-1.5-flash"
    max_tokens: int = 2000
    temperature: float = 0.7

class ServiceUrls(BaseSettings):
    """
    Service URLs for communication between different services.
    """
    ai_agent: str = "http://localhost:8002"
    metadata_processor: str = "http://localhost:8001"
    catalog_api: str = "http://localhost:8003"

class DataSourceConfig(BaseSettings):
    """
    Configuration for each data source.
    """
    name: str
    type: str
    config: dict = {}

class Settings(BaseSettings):
    """
    Main application settings class.
    """
    ai: AiSettings = AiSettings() 
    services: ServiceUrls = ServiceUrls()
    data_sources: list[DataSourceConfig] = [
        DataSourceConfig(name="excel-upload", type="excel"),
        DataSourceConfig(name="sql-ddl-source", type="sql_ddl"),
        DataSourceConfig(name="starburst-connector", type="starburst"),
        DataSourceConfig(name="image-diagram-processor", type="image_diagram"),
        DataSourceConfig(name="sql-lineage-parser", type="sql_lineage"),
    ]

settings = Settings()
