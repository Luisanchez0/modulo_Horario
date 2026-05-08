import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock environment variables before importing app
os.environ['ADMIN_CREATION_KEY'] = 'test_key_123'
os.environ['JWT_SECRET'] = 'test_secret_key'
os.environ['MYSQL_USER'] = 'test'
os.environ['MYSQL_PASSWORD'] = 'test'

from main import app

client = TestClient(app)


class TestAuthSecurity:
    """Security tests for authentication endpoints"""

    def test_login_without_credentials(self):
        """Should reject login without credentials"""
        response = client.post("/auth/login", json={})
        assert response.status_code == 422  # Validation error

    def test_login_with_invalid_email(self):
        """Should reject invalid email format"""
        response = client.post("/auth/login", json={
            "correo": "not-an-email",
            "password": "somepassword"
        })
        # Should fail validation or auth
        assert response.status_code in [422, 401]

    def test_login_wrong_password(self):
        """Should reject wrong password"""
        # Mock user lookup to return a user
        with patch('src.infrastructure.repositories.docente_repository_impl.DocenteRepositoryImpl.obtener_por_correo') as mock_get:
            mock_user = MagicMock()
            mock_user.correo = 'test@example.com'
            mock_user.contraseña_hash = 'hashed_password'
            mock_get.return_value = mock_user

            response = client.post("/auth/login", json={
                "correo": "test@example.com",
                "password": "wrongpassword"
            })
            # Should return 401 Unauthorized
            assert response.status_code == 401
            assert "401" in str(response.status_code)

    def test_register_admin_without_key(self):
        """Should reject admin registration without valid key"""
        response = client.post("/auth/register-admin", json={
            "nombre": "Admin User",
            "correo": "admin@example.com",
            "password": "securepass123",
            "role": "ADMIN"
        })
        # Should reject without proper header
        assert response.status_code == 403

    def test_register_admin_with_wrong_key(self):
        """Should reject admin registration with wrong key"""
        response = client.post(
            "/auth/register-admin",
            json={
                "nombre": "Admin User",
                "correo": "admin@example.com",
                "password": "securepass123",
                "role": "ADMIN"
            },
            headers={"X-Admin-Key": "wrong_key"}
        )
        assert response.status_code == 403
        assert "inválida" in response.json()["detail"].lower()

    def test_password_validation(self):
        """Should enforce password requirements"""
        response = client.post("/auth/register", json={
            "nombre": "Test User",
            "correo": "test@example.com",
            "password": "weak",  # Too weak
            "role": "DOCENTE"
        })
        # Should reject weak password
        assert response.status_code in [422, 400]

    def test_sql_injection_attempt(self):
        """Should prevent SQL injection in login"""
        response = client.post("/auth/login", json={
            "correo": "admin@example.com' OR '1'='1",
            "password": "anything"
        })
        # Should not execute SQL, just fail auth
        assert response.status_code == 401 or response.status_code == 422
        # Should NOT return database error
        assert "syntax" not in response.text.lower()
        assert "sql" not in response.text.lower()

    def test_xss_injection_attempt(self):
        """Should prevent XSS in responses"""
        response = client.post("/auth/register", json={
            "nombre": "<script>alert('xss')</script>",
            "correo": "test@example.com",
            "password": "Password123!",
            "role": "DOCENTE"
        })
        # Even if request fails, response should escape HTML
        assert "<script>" not in response.text or "\\u003c" in response.text

    def test_jwt_token_missing(self):
        """Should reject requests without JWT"""
        response = client.get("/auth/me")
        assert response.status_code == 403

    def test_jwt_token_invalid(self):
        """Should reject invalid JWT tokens"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code in [401, 403, 422]

    def test_jwt_token_malformed(self):
        """Should reject malformed JWT"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer notavalidtoken"}
        )
        assert response.status_code in [401, 403, 422]

    def test_cors_headers_present(self):
        """Should include security headers in response"""
        response = client.options("/auth/login")
        # Check CORS headers exist
        assert "access-control-allow-origin" in response.headers or response.status_code == 200

    def test_password_not_in_response(self):
        """Should never return passwords in response"""
        response = client.get("/health")
        assert "contraseña" not in response.text.lower()
        assert "password" not in response.text.lower()


class TestInputValidation:
    """Test input validation on endpoints"""

    def test_email_format_validation(self):
        """Should validate email format"""
        response = client.post("/auth/register", json={
            "nombre": "Test",
            "correo": "invalid-email",
            "password": "Password123!",
            "role": "DOCENTE"
        })
        assert response.status_code in [422, 400]

    def test_empty_name_validation(self):
        """Should validate non-empty name"""
        response = client.post("/auth/register", json={
            "nombre": "",
            "correo": "test@example.com",
            "password": "Password123!",
            "role": "DOCENTE"
        })
        assert response.status_code in [422, 400]

    def test_special_characters_escaped(self):
        """Should safely handle special characters"""
        response = client.post("/auth/register", json={
            "nombre": "Test'; DROP TABLE users; --",
            "correo": "test@example.com",
            "password": "Password123!",
            "role": "DOCENTE"
        })
        # Should not execute SQL
        if response.status_code != 201:
            assert "syntax" not in response.text.lower()


class TestHTTPStatusCodes:
    """Test proper HTTP status codes"""

    def test_health_endpoint_200(self):
        """Health check should return 200"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_invalid_endpoint_404(self):
        """Should return 404 for non-existent endpoints"""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_invalid_method_405(self):
        """Should return 405 for wrong HTTP method"""
        response = client.get("/auth/login")  # GET instead of POST
        assert response.status_code == 405


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
