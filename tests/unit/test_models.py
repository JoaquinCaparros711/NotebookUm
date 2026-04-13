"""Unit tests for database models."""

import pytest
from datetime import datetime, UTC
from app import create_app
from app.database import db
from app.models.document import HistorialDocumento
from app.models.user import User


def _try_import_historial_pregunta_model():
    try:
        from app.models.question import HistorialPregunta
    except ModuleNotFoundError as exc:
        if exc.name == "app.models.question":
            return None
        raise
    return HistorialPregunta


def _require_historial_pregunta_model():
    model = _try_import_historial_pregunta_model()
    if model is None:
        pytest.fail("HistorialPregunta no existe todavia. Implementar en app/models/question.py (T077).")
    return model


@pytest.fixture
def app():
    """Create and configure a test application instance"""
    app = create_app("testing")

    with app.app_context():
        # Ensure optional models are imported (so db.create_all creates their tables when present).
        _try_import_historial_pregunta_model()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def session(app):
    """Create a database session for tests"""
    with app.app_context():
        yield db.session


@pytest.mark.unit
class TestUserModel:
    """Unit tests for User model"""

    def test_user_creation(self, session):
        """Test successful user model creation"""
        # Given: Valid user data
        email = "model_test@example.com"
        nombre = "Model Test User"

        # When: Creating a User instance and saving to database
        user = User(email=email, nombre=nombre)
        session.add(user)
        session.commit()

        # Then: User is created with correct attributes
        assert user.id is not None
        assert user.email == email
        assert user.nombre == nombre
        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_user_email_uniqueness(self, session):
        """Test that email uniqueness constraint is enforced"""
        # Given: A user with a specific email
        email = "unique@example.com"
        user1 = User(email=email, nombre="First User")
        session.add(user1)
        session.commit()

        # When: Attempting to create another user with the same email
        user2 = User(email=email, nombre="Second User")
        session.add(user2)

        # Then: Database raises IntegrityError due to unique constraint
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            session.commit()

    def test_user_timestamps_created_and_updated(self, session):
        """Test that created_at and updated_at timestamps are set correctly"""
        # Given: A new user
        user = User(email="timestamp_test@example.com", nombre="Timestamp User")
        
        # When: Saving to database
        session.add(user)
        session.commit()
        
        created_at = user.created_at
        updated_at = user.updated_at

        # Then: Both timestamps are set
        assert created_at is not None
        assert updated_at is not None
        
        # Then: Both timestamps are very close (within 1 second, allowing for microseconds difference)
        time_diff = abs((updated_at - created_at).total_seconds())
        assert time_diff < 1.0
        
        # Then: Timestamps are datetime objects
        assert isinstance(created_at, datetime)
        assert isinstance(updated_at, datetime)

    def test_user_to_dict(self, session):
        """Test that to_dict method returns correct dictionary representation"""
        # Given: A user in the database
        user = User(email="dict_test@example.com", nombre="Dict Test User")
        session.add(user)
        session.commit()

        # When: Converting user to dictionary
        user_dict = user.to_dict()

        # Then: Dictionary contains all required fields
        assert "id" in user_dict
        assert "email" in user_dict
        assert "nombre" in user_dict
        assert "created_at" in user_dict
        assert "updated_at" in user_dict
        
        # Then: Dictionary values are correct
        assert user_dict["id"] == user.id
        assert user_dict["email"] == "dict_test@example.com"
        assert user_dict["nombre"] == "Dict Test User"
        
        # Then: Timestamps are ISO format strings
        assert isinstance(user_dict["created_at"], str)
        assert isinstance(user_dict["updated_at"], str)


@pytest.mark.unit
class TestHistorialPreguntaModel:
    """Unit tests for HistorialPregunta model."""

    def test_historial_pregunta_creation_and_relationships(self, session):
        """HistorialPregunta must persist with required fields and relationships."""
        HistorialPregunta = _require_historial_pregunta_model()

        user = User(email="hist_pregunta_user@example.com", nombre="Hist Pregunta User")
        session.add(user)
        session.commit()

        document = HistorialDocumento(
            usuario_id=user.id,
            nombre_archivo="hist_pregunta.pdf",
            tamanio_bytes=1234,
        )
        session.add(document)
        session.commit()

        pregunta = HistorialPregunta(
            usuario_id=user.id,
            documento_id=document.id,
            pregunta="Que dice el documento?",
            respuesta=None,
        )
        session.add(pregunta)
        session.commit()

        assert pregunta.id is not None
        assert pregunta.usuario_id == user.id
        assert pregunta.documento_id == document.id
        assert pregunta.pregunta == "Que dice el documento?"
        assert pregunta.respuesta is None
        assert pregunta.created_at is not None
        assert isinstance(pregunta.created_at, datetime)

        # Expected convenience aliases for API compatibility (like Summary model).
        assert getattr(pregunta, "user_id") == user.id
        assert getattr(pregunta, "document_id") == document.id

        assert pregunta.usuario.id == user.id
        assert pregunta.documento.id == document.id

    def test_historial_pregunta_to_dict(self, session):
        """to_dict should include both Spanish and API-friendly keys."""
        HistorialPregunta = _require_historial_pregunta_model()

        user = User(email="hist_pregunta_dict@example.com", nombre="Hist Pregunta Dict")
        session.add(user)
        session.commit()

        document = HistorialDocumento(
            usuario_id=user.id,
            nombre_archivo="hist_pregunta_dict.pdf",
            tamanio_bytes=5678,
        )
        session.add(document)
        session.commit()

        pregunta = HistorialPregunta(
            usuario_id=user.id,
            documento_id=document.id,
            pregunta="Pregunta dict",
            respuesta="Respuesta dict",
        )
        session.add(pregunta)
        session.commit()

        payload = pregunta.to_dict()

        assert payload["id"] == pregunta.id
        assert payload["usuario_id"] == user.id
        assert payload["documento_id"] == document.id
        assert payload["pregunta"] == "Pregunta dict"
        assert payload["respuesta"] == "Respuesta dict"
        assert isinstance(payload["created_at"], str)

        assert payload["user_id"] == user.id
        assert payload["document_id"] == document.id
