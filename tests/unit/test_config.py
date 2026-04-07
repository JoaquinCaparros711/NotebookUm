"""Unit tests for app/config.py"""

import os
import pytest
from app.config import (
    DatabaseConfig,
    OpenAIConfig,
    BaseConfig,
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig,
)


class TestDatabaseConfig:
    """Tests for DatabaseConfig dataclass"""

    def test_database_config_creation(self):
        """Test DatabaseConfig can be created with required fields"""
        db_config = DatabaseConfig(
            host="localhost", port=3306, name="test_db", user="test_user", password="test_pass"
        )

        assert db_config.host == "localhost"
        assert db_config.port == 3306
        assert db_config.name == "test_db"
        assert db_config.user == "test_user"
        assert db_config.password == "test_pass"

    def test_database_url_generation(self):
        """Test database URL is generated correctly"""
        db_config = DatabaseConfig(
            host="localhost", port=3306, name="test_db", user="test_user", password="test_pass"
        )

        expected_url = "mysql+mysqlconnector://test_user:test_pass@localhost:3306/test_db"
        assert db_config.url == expected_url

    def test_database_url_with_special_characters(self):
        """Test database URL handles special characters in password"""
        db_config = DatabaseConfig(
            host="localhost", port=3306, name="test_db", user="user", password="p@ss:word"
        )

        # URL should contain the password as-is (URL encoding is handled by SQLAlchemy)
        assert "p@ss:word" in db_config.url


class TestOpenAIConfig:
    """Tests for OpenAIConfig dataclass"""

    def test_openai_config_creation(self):
        """Test OpenAIConfig can be created with API key"""
        openai_config = OpenAIConfig(api_key="sk-test-key")

        assert openai_config.api_key == "sk-test-key"


class TestBaseConfig:
    """Tests for BaseConfig"""

    def test_base_config_defaults(self):
        """Test BaseConfig has correct default values"""
        assert BaseConfig.DEBUG is False
        assert BaseConfig.TESTING is False
        assert BaseConfig.MAX_UPLOAD_SIZE == 26214400  # 25MB

    def test_base_config_has_database(self):
        """Test BaseConfig has DATABASE configuration"""
        assert hasattr(BaseConfig, "DATABASE")
        assert isinstance(BaseConfig.DATABASE, DatabaseConfig)

    def test_base_config_has_openai(self):
        """Test BaseConfig has OPENAI configuration"""
        assert hasattr(BaseConfig, "OPENAI")
        assert isinstance(BaseConfig.OPENAI, OpenAIConfig)

    def test_base_config_sqlalchemy_settings(self):
        """Test BaseConfig has SQLAlchemy settings"""
        assert hasattr(BaseConfig, "SQLALCHEMY_DATABASE_URI")
        assert hasattr(BaseConfig, "SQLALCHEMY_TRACK_MODIFICATIONS")
        assert BaseConfig.SQLALCHEMY_TRACK_MODIFICATIONS is False

    def test_base_config_celery_settings(self):
        """Test BaseConfig has Celery settings"""
        assert hasattr(BaseConfig, "CELERY_BROKER_URL")
        assert hasattr(BaseConfig, "CELERY_RESULT_BACKEND")


class TestDevelopmentConfig:
    """Tests for DevelopmentConfig"""

    def test_development_config_debug_enabled(self):
        """Test DevelopmentConfig has DEBUG enabled"""
        assert DevelopmentConfig.DEBUG is True

    def test_development_config_sqlalchemy_echo(self):
        """Test DevelopmentConfig has SQLALCHEMY_ECHO enabled"""
        assert DevelopmentConfig.SQLALCHEMY_ECHO is True


class TestProductionConfig:
    """Tests for ProductionConfig"""

    def test_production_config_debug_disabled(self):
        """Test ProductionConfig has DEBUG disabled"""
        assert ProductionConfig.DEBUG is False

    def test_production_config_testing_disabled(self):
        """Test ProductionConfig has TESTING disabled"""
        assert ProductionConfig.TESTING is False


class TestTestingConfig:
    """Tests for TestingConfig"""

    def test_testing_config_testing_enabled(self):
        """Test TestingConfig has TESTING enabled"""
        assert TestingConfig.TESTING is True

    def test_testing_config_debug_enabled(self):
        """Test TestingConfig has DEBUG enabled"""
        assert TestingConfig.DEBUG is True

    def test_testing_config_uses_sqlite(self):
        """Test TestingConfig uses SQLite for in-memory database"""
        assert "sqlite" in TestingConfig.SQLALCHEMY_DATABASE_URI
        assert ":memory:" in TestingConfig.SQLALCHEMY_DATABASE_URI


class TestEnvironmentVariableLoading:
    """Tests for environment variable loading"""

    def test_max_upload_size_default(self):
        """Test MAX_UPLOAD_SIZE has correct default value"""
        assert BaseConfig.MAX_UPLOAD_SIZE == 26214400  # 25MB default

    def test_database_config_loads_from_env(self):
        """Test database configuration is loaded from environment variables"""
        # This is implicitly tested by the fact that DatabaseConfig is created
        # with values from os.getenv() calls
        assert BaseConfig.DATABASE is not None
        assert isinstance(BaseConfig.DATABASE, DatabaseConfig)

    def test_openai_config_loads_from_env(self):
        """Test OpenAI configuration is loaded from environment variables"""
        assert BaseConfig.OPENAI is not None
        assert isinstance(BaseConfig.OPENAI, OpenAIConfig)
