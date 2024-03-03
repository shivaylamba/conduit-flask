import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
import jwt
import os

class TestAuthenticationMiddleware(unittest.TestCase):

    def setUp(self):
        # Create a Flask app for testing
        self.app = Flask(__name__)
        os.environ['SECRET'] = 'test_secret_key'

    def test_authenticate_with_valid_token(self):
        # Mock the request headers with a valid token
        with self.app.test_request_context(headers={'Authorization': 'valid_token'}):
            with patch('models.users.User.get_user_by_id') as mock_get_user_by_id:
                # Mock the User.get_user_by_id method
                mock_user = MagicMock()
                mock_get_user_by_id.return_value = mock_user

                # Call the authenticate function
                from ..utils.auth import authenticate
                authenticate()

                # Assert that g.current_user is set to the mock user
                self.assertEqual(g.current_user, mock_user)

    def test_authenticate_with_expired_token(self):
        # Mock the request headers with an expired token
        with self.app.test_request_context(headers={'Authorization': 'expired_token'}):
            with patch('jwt.decode') as mock_decode:
                # Mock the jwt.decode method to raise ExpiredSignatureError
                mock_decode.side_effect = jwt.ExpiredSignatureError('Expired Token')

                # Call the authenticate function
                from ..utils.auth import authenticate
                response = authenticate()

                # Assert that the response contains the expected error message and status code
                self.assertEqual(response.status_code, 401)
                self.assertIn('Token has expired', response.get_json()['error'])

    def test_authenticate_with_invalid_token(self):
        # Mock the request headers with an invalid token
        with self.app.test_request_context(headers={'Authorization': 'invalid_token'}):
            with patch('jwt.decode') as mock_decode:
                # Mock the jwt.decode method to raise InvalidTokenError
                mock_decode.side_effect = jwt.InvalidTokenError('Invalid Token')

                # Call the authenticate function
                from ..utils.auth import authenticate
                response = authenticate()

                # Assert that the response contains the expected error message and status code
                self.assertEqual(response.status_code, 401)
                self.assertIn('Invalid token', response.get_json()['error'])

    def test_authenticate_with_no_token(self):
        # Mock the request headers with no token
        with self.app.test_request_context():
            # Call the authenticate function
            from ..utils.auth import authenticate
            response = authenticate()

            # Assert that the response contains the expected error message and status code
            self.assertEqual(response.status_code, 401)
            self.assertIn('Authorization token required', response.get_json()['error'])


import unittest
from unittest.mock import patch, MagicMock
from utils.jwt import generate_token
from datetime import datetime, timedelta

class TestGenerateToken(unittest.TestCase):

    @patch('utils.jwt.datetime')
    @patch('utils.jwt.jwt.encode')
    def test_generate_token(self, mock_jwt_encode, mock_datetime):
        # Mock current datetime to a fixed value for consistent testing
        mock_now = datetime(2022, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now

        # Mock the jwt.encode method
        mock_encoded_token = MagicMock()
        mock_jwt_encode.return_value = mock_encoded_token

        # Call the generate_token function with a mock user_id
        user_id = 'mock_user_id'
        token = generate_token(user_id)

        # Assertions
        mock_datetime.utcnow.assert_called_once()
        mock_jwt_encode.assert_called_once_with(
            {'user_id': user_id, 'exp': mock_now + timedelta(days=15)},
            'mock_secret_key', algorithm='HS256'
        )
        self.assertEqual(token, mock_encoded_token)

import unittest
from utils.slug import create_slug

class TestCreateSlug(unittest.TestCase):

    def test_create_slug_basic(self):
        # Test with a simple title
        title = "Hello World"
        expected_slug = "hello-world"
        result_slug = create_slug(title)
        self.assertEqual(result_slug, expected_slug)

    def test_create_slug_special_characters(self):
        # Test with a title containing special characters
        title = "!@#$%^&*() Hello 123 World!?"
        expected_slug = "hello-123-world"
        result_slug = create_slug(title)
        self.assertEqual(result_slug, expected_slug)

    def test_create_slug_edge_cases(self):
        # Test with an empty title
        title = ""
        expected_slug = ""
        result_slug = create_slug(title)
        self.assertEqual(result_slug, expected_slug)

        # Test with a title containing only spaces
        title = "    "
        expected_slug = ""
        result_slug = create_slug(title)
        self.assertEqual(result_slug, expected_slug)

    def test_create_slug_unicode_characters(self):
        # Test with a title containing Unicode characters
        title = "Héllo Wörld"
        expected_slug = "hello-world"
        result_slug = create_slug(title)
        self.assertEqual(result_slug, expected_slug)