import pytest
from library import Book, fetch_book_details_by_isbn
from unittest.mock import patch


def test_book_creation():
    book = Book("The Hobbit", "J.R.R. Tolkien", "978-0345339683")
    assert book.title == "The Hobbit"
    assert book.author == "J.R.R. Tolkien"
    assert book.is_borrowed is False


def test_borrow_and_return_logic():
    book = Book("Dune", "Frank Herbert", "978-0441013593")

    book.borrow_book()
    assert book.is_borrowed is True

    book.return_book()
    assert book.is_borrowed is False


def test_cannot_borrow_twice():
    book = Book("1984", "George Orwell", "978-0451524935")
    book.borrow_book()
    with pytest.raises(ValueError):
        book.borrow_book()


def test_cannot_return_if_not_borrowed():
    book = Book("1984", "George Orwell", "978-0451524935")
    with pytest.raises(ValueError):
        book.return_book()


@patch("library.requests.get")
def test_fetch_book_details_by_isbn_success(mock_get):
    mock_get.return_value.raise_for_status.return_value = None
    mock_get.return_value.json.return_value = {
        "ISBN:9780140328721": {
            "title": "Matilda",
            "authors": [{"name": "Roald Dahl"}]
        }
    }

    result = fetch_book_details_by_isbn("9780140328721")
    assert result == ("Matilda", "Roald Dahl")


@patch("library.requests.get")
def test_fetch_book_details_by_isbn_not_found(mock_get):
    mock_get.return_value.raise_for_status.return_value = None
    mock_get.return_value.json.return_value = {}

    result = fetch_book_details_by_isbn("0000000000")
    assert result is None


@patch("library.requests.get")
def test_fetch_book_details_by_isbn_network_error(mock_get):
    mock_get.side_effect = Exception("network")
    result = fetch_book_details_by_isbn("9780140328721")
    assert result is None


