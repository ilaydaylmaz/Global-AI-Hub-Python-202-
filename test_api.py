"""
API Tests for Library Management System
Tests for FastAPI endpoints using pytest and httpx
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import json
import os
from api import app, DATA_FILE

client = TestClient(app)

# Test data
VALID_ISBN = "9780140328721"
INVALID_ISBN = "0000000000"
MOCK_BOOK_DATA = ("Test Book Title", "Test Author")

@pytest.fixture(autouse=True)
def cleanup_test_data(monkeypatch):
    """Clean up test data files and reset library state before and after each test."""
    import uuid
    from library import Library
    test_file = f"test_api_library_{uuid.uuid4().hex[:8]}.json"
    
    # Patch the DATA_FILE constant in the api module
    monkeypatch.setattr("api.DATA_FILE", test_file)
    
    # Reset the library instance to be empty for each test
    fresh_library = Library("Test Library")
    monkeypatch.setattr("api.library", fresh_library)
    
    # Clean up before test
    if os.path.exists(test_file):
        os.remove(test_file)
    
    yield
    
    # Clean up after test
    if os.path.exists(test_file):
        os.remove(test_file)

def test_root_endpoint():
    """Test the root endpoint returns basic info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data
    assert "total_books" in data

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "library_name" in data

def test_get_books_empty():
    """Test GET /books returns empty list initially."""
    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == []

@patch("api.fetch_book_details_by_isbn")
def test_add_book_success(mock_fetch):
    """Test POST /books successfully adds a book."""
    mock_fetch.return_value = MOCK_BOOK_DATA
    
    response = client.post("/books", json={"isbn": VALID_ISBN})
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "Test Book Title"
    assert data["author"] == "Test Author"
    assert data["isbn"] == VALID_ISBN
    assert data["is_borrowed"] == False
    assert data["book_type"] == "Book"

@patch("api.fetch_book_details_by_isbn")
def test_add_book_not_found(mock_fetch):
    """Test POST /books with ISBN not found in Open Library."""
    mock_fetch.return_value = None
    
    response = client.post("/books", json={"isbn": INVALID_ISBN})
    assert response.status_code == 404
    assert "not found in Open Library" in response.json()["detail"]

def test_add_book_empty_isbn():
    """Test POST /books with empty ISBN."""
    response = client.post("/books", json={"isbn": ""})
    assert response.status_code == 400
    assert "ISBN cannot be empty" in response.json()["detail"]

@patch("api.fetch_book_details_by_isbn")
def test_add_duplicate_book(mock_fetch):
    """Test POST /books with duplicate ISBN."""
    mock_fetch.return_value = MOCK_BOOK_DATA
    
    # Add book first time
    response1 = client.post("/books", json={"isbn": VALID_ISBN})
    assert response1.status_code == 200
    
    # Try to add same book again
    response2 = client.post("/books", json={"isbn": VALID_ISBN})
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"]

@patch("api.fetch_book_details_by_isbn")
def test_get_books_with_data(mock_fetch):
    """Test GET /books returns list of books after adding some."""
    mock_fetch.return_value = MOCK_BOOK_DATA
    
    # Add a book
    client.post("/books", json={"isbn": VALID_ISBN})
    
    # Get all books
    response = client.get("/books")
    assert response.status_code == 200
    
    books = response.json()
    assert len(books) == 1
    assert books[0]["isbn"] == VALID_ISBN

@patch("api.fetch_book_details_by_isbn")
def test_get_book_by_isbn(mock_fetch):
    """Test GET /books/{isbn} returns specific book."""
    mock_fetch.return_value = MOCK_BOOK_DATA
    
    # Add a book
    client.post("/books", json={"isbn": VALID_ISBN})
    
    # Get specific book
    response = client.get(f"/books/{VALID_ISBN}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["isbn"] == VALID_ISBN
    assert data["title"] == "Test Book Title"

def test_get_book_by_isbn_not_found():
    """Test GET /books/{isbn} with non-existent ISBN."""
    response = client.get(f"/books/{INVALID_ISBN}")
    assert response.status_code == 404
    assert "not found in library" in response.json()["detail"]

@patch("api.fetch_book_details_by_isbn")
def test_delete_book_success(mock_fetch):
    """Test DELETE /books/{isbn} successfully removes book."""
    mock_fetch.return_value = MOCK_BOOK_DATA
    
    # Add a book
    client.post("/books", json={"isbn": VALID_ISBN})
    
    # Delete the book
    response = client.delete(f"/books/{VALID_ISBN}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] == True
    assert "successfully removed" in data["message"]
    
    # Verify book is gone
    get_response = client.get(f"/books/{VALID_ISBN}")
    assert get_response.status_code == 404

def test_delete_book_not_found():
    """Test DELETE /books/{isbn} with non-existent ISBN."""
    response = client.delete(f"/books/{INVALID_ISBN}")
    assert response.status_code == 404
    assert "not found in library" in response.json()["detail"]

def test_delete_book_empty_isbn():
    """Test DELETE /books/{isbn} with empty ISBN."""
    response = client.delete("/books/ ")  # Space gets stripped
    assert response.status_code == 400
    assert "ISBN cannot be empty" in response.json()["detail"]

@patch("api.fetch_book_details_by_isbn")
def test_full_workflow(mock_fetch):
    """Test complete workflow: add, get, delete."""
    mock_fetch.return_value = MOCK_BOOK_DATA
    
    # 1. Start with empty library
    response = client.get("/books")
    assert len(response.json()) == 0
    
    # 2. Add a book
    add_response = client.post("/books", json={"isbn": VALID_ISBN})
    assert add_response.status_code == 200
    
    # 3. Verify book exists
    get_response = client.get("/books")
    assert len(get_response.json()) == 1
    
    # 4. Delete the book
    delete_response = client.delete(f"/books/{VALID_ISBN}")
    assert delete_response.status_code == 200
    
    # 5. Verify library is empty again
    final_response = client.get("/books")
    assert len(final_response.json()) == 0

def test_api_persistence():
    """Test that API data persists to file."""
    with patch("api.fetch_book_details_by_isbn") as mock_fetch:
        mock_fetch.return_value = MOCK_BOOK_DATA
        
        # Add a book
        response = client.post("/books", json={"isbn": VALID_ISBN})
        assert response.status_code == 200
        
        # Get the current DATA_FILE from the api module (which was patched in fixture)
        from api import DATA_FILE
        
        # Check that data file was created
        assert os.path.exists(DATA_FILE)
        
        # Verify file contents
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            assert len(data["books"]) == 1
            assert data["books"][0]["isbn"] == VALID_ISBN
