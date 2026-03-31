import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = False
    TESTING = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    # Use real API keys from .env for integration tests
    GEMMA_API_KEY = os.getenv("GEMMA_API_KEY")
    GEMMA_API_URL = os.getenv("GEMMA_API_URL")


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
