import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration using dataclass"""

    host: str
    port: int
    name: str
    user: str
    password: str

    @property
    def url(self) -> str:
        """Generate SQLAlchemy database URL"""
        return f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class OpenAIConfig:
    """OpenAI API configuration using dataclass"""

    api_key: str


class BaseConfig:
    """Base configuration class with common settings"""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = False
    TESTING = False
    MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 26214400))  # 25MB default

    # Database configuration
    DATABASE = DatabaseConfig(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        name=os.getenv("DB_NAME", "notebookum"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
    )

    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = DATABASE.url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # OpenAI configuration
    OPENAI = OpenAIConfig(api_key=os.getenv("OPENAI_API_KEY", ""))

    # Celery configuration
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")


class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""

    DEBUG = True
    SQLALCHEMY_ECHO = True  # Log SQL queries in development


class ProductionConfig(BaseConfig):
    """Production environment configuration"""

    DEBUG = False
    TESTING = False


class TestingConfig(BaseConfig):
    """Testing environment configuration"""

    TESTING = True
    DEBUG = True
    # Use in-memory SQLite for tests
    DATABASE = DatabaseConfig(
        host="localhost", port=3306, name=":memory:", user="test", password="test"
    )
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Use a dummy OpenAI API key for testing
    OPENAI = OpenAIConfig(api_key="sk-test-dummy-key-for-testing")


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
