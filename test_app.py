import os
import tempfile
import pytest
from app import app, db


@pytest.fixture
def client():
    """
    Setup a test client and temporary database for testing.
    """
    db_fd, temp_db = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{temp_db}"
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

    os.close(db_fd)
    os.unlink(temp_db)


def test_home_page(client):
    """
    Test if the home page is accessible.
    """
    response = client.get('/')
    assert response.status_code == 200


def test_upload_invalid_file_type(client):
    """
    Test uploading a file with an invalid extension.
    """
    with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_file:
        temp_file.write(b"Sample content")
        temp_file.flush()

        with open(temp_file.name, 'rb') as file:
            data = {
                'file': (file, 'test_invalid.pdf')
            }
            response = client.post(
                '/',
                data=data,
                content_type='multipart/form-data'
            )

        assert response.status_code == 400
        assert b"Invalid file type" in response.data


def test_upload_duplicate_file(client):
    """
    Test uploading a duplicate file.
    """
    with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
        temp_file.write(b"Sample content")
        temp_file.flush()

        with open(temp_file.name, 'rb') as file:
            data = {
                'file': (file, 'test_duplicate.txt')
            }
            # First upload
            client.post('/', data=data, content_type='multipart/form-data')

        with open(temp_file.name, 'rb') as file:
            data = {
                'file': (file, 'test_duplicate.txt')
            }
            # Attempt to upload the same file again
            response = client.post(
                '/',
                data=data,
                content_type='multipart/form-data'
            )

        assert response.status_code == 409
        assert b"File with this name already exists" in response.data


def test_list_files(client):
    """
    Test listing files with their classified data.
    """
    with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
        temp_file.write(b"Sample content")
        temp_file.flush()

        with open(temp_file.name, 'rb') as file:
            data = {
                'file': (file, 'test_list.txt')
            }
            # Upload a file first
            client.post('/', data=data, content_type='multipart/form-data')

        # Check the listing page
        response = client.get('/list')
        assert response.status_code == 200
        assert b"test_list.txt" in response.data
