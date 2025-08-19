"""
Python ile Nesne Yönelimli Programlama (OOP): Kütüphane Sistemi
Bu dosya, OOP notebook'undaki tüm kod örneklerini içerir.
"""

from dataclasses import dataclass, field
from typing import List
from pydantic import BaseModel, Field, ValidationError
import requests
import json
import os


class Book:
    """Represents a single book in our library."""
    def __init__(self, title: str, author: str, isbn: str):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.is_borrowed = False

    def borrow_book(self):
        """Marks the book as borrowed."""
        if not self.is_borrowed:
            self.is_borrowed = True
        else:
            # Raise an error if already borrowed for clear feedback
            raise ValueError(f"'{self.title}' is already borrowed.")

    def return_book(self):
        """Marks the book as returned."""
        if self.is_borrowed:
            self.is_borrowed = False
        else:
            raise ValueError(f"'{self.title}' was not borrowed.")

    def display_info(self) -> str:
        return f"'{self.title}' by {self.author}"


class EBook(Book):
    """Represents an electronic book that inherits from Book."""
    def __init__(self, title: str, author: str, isbn: str, file_format: str):
        super().__init__(title, author, isbn)
        self.file_format = file_format

    def display_info(self) -> str:
        return f"{super().display_info()} [Format: {self.file_format}]"


class AudioBook(Book):
    """Represents an audio book that inherits from Book."""
    def __init__(self, title: str, author: str, isbn: str, duration_in_minutes: int):
        super().__init__(title, author, isbn)
        self.duration = duration_in_minutes

    def display_info(self) -> str:
        return f"{super().display_info()} [Duration: {self.duration} mins]"


class Library:
    """Manages a collection of books using composition."""
    def __init__(self, name: str):
        self.name = name
        # Encapsulation: Bu liste sınıfın iç detayıdır.
        self._books = []

    def add_book(self, book: 'Book'):
        self._books.append(book)

    def find_book(self, title: str) -> 'Book | None':
        for book in self._books:
            if book.title.lower() == title.lower():
                return book
        return None

    def find_book_by_isbn(self, isbn: str) -> 'Book | None':
        for book in self._books:
            if book.isbn == isbn:
                return book
        return None

    def remove_book_by_isbn(self, isbn: str) -> bool:
        target = self.find_book_by_isbn(isbn)
        if target is None:
            return False
        self._books.remove(target)
        return True

    def list_books(self) -> list['Book']:
        return list(self._books)

    @property
    def total_books(self) -> int:
        return len(self._books)

    # --- Persistence helpers ---
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "books": [self._serialize_book(b) for b in self._books],
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Library':
        name = data.get("name", "Library")
        lib = cls(name=name)
        for b in data.get("books", []):
            book = cls._deserialize_book(b)
            if book:
                lib.add_book(book)
        return lib

    def save_to_file(self, file_path: str) -> None:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception:
            # Sessizce geç; CLI kullanıcı deneyimini bozma
            pass

    @classmethod
    def load_from_file(cls, file_path: str, default_name: str = "Library") -> 'Library':
        if not os.path.exists(file_path):
            return cls(name=default_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception:
            return cls(name=default_name)

    @staticmethod
    def _serialize_book(book: 'Book') -> dict:
        kind = book.__class__.__name__
        base = {
            "kind": kind,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "is_borrowed": getattr(book, "is_borrowed", False),
        }
        if kind == "EBook":
            base["file_format"] = getattr(book, "file_format", "")
        if kind == "AudioBook":
            base["duration"] = getattr(book, "duration", 0)
        return base

    @staticmethod
    def _deserialize_book(data: dict) -> 'Book | None':
        try:
            kind = data.get("kind", "Book")
            title = data.get("title", "")
            author = data.get("author", "")
            isbn = data.get("isbn", "")
            is_borrowed = bool(data.get("is_borrowed", False))
            if kind == "EBook":
                file_format = data.get("file_format", "")
                b = EBook(title=title, author=author, isbn=isbn, file_format=file_format)
            elif kind == "AudioBook":
                duration = int(data.get("duration", 0))
                b = AudioBook(title=title, author=author, isbn=isbn, duration_in_minutes=duration)
            else:
                b = Book(title=title, author=author, isbn=isbn)
            b.is_borrowed = is_borrowed
            return b
        except Exception:
            return None


@dataclass
class Member:
    """Represents a library member using dataclasses."""
    name: str
    member_id: int
    borrowed_books: List[Book] = field(default_factory=list)


class PydanticBook(BaseModel):
    """Book model with Pydantic validation."""
    title: str
    author: str
    isbn: str = Field(..., min_length=10, max_length=13)
    publication_year: int = Field(..., gt=1400)  # 1400'den büyük olmalı


def main():
    """Demo function to show the library system in action."""
    print("=== Kütüphane Sistemi Demo ===\n")

    # Create different types of books
    ebook = EBook("1984", "George Orwell", "978-0451524935", "EPUB")
    audio_book = AudioBook("Becoming", "Michelle Obama", "978-1524763138", 780)
    regular_book = Book("The Lord of the Rings", "J.R.R. Tolkien", "978-0618640157")

    print(f"{ebook.title} formatı: {ebook.file_format}")
    print(f"{audio_book.title} süresi: {audio_book.duration} dakika\n")

    # Create library and add books (Composition)
    my_library = Library(name="City Library")
    my_library.add_book(ebook)
    my_library.add_book(audio_book)
    my_library.add_book(regular_book)

    print(f"{my_library.name} kütüphanesindeki toplam kitap sayısı: {my_library.total_books}")

    # Find a book
    found_book = my_library.find_book("1984")
    if found_book:
        print(f"Bulunan kitap: {found_book.title} by {found_book.author}\n")

    # Demonstrate Polymorphism
    print("=== Polimorfizm Örneği ===")
    book_list = [regular_book, ebook, audio_book]

    for book in book_list:
        print(book.display_info())

    print("\n=== Dataclass Örneği ===")
    # Create a member using dataclasses
    member1 = Member(name="Alice", member_id=101)
    print(member1)

    print("\n=== Pydantic Doğrulama Örneği ===")
    # Pydantic validation example
    try:
        valid_book = PydanticBook(
            title="Dune",
            author="Frank Herbert",
            isbn="9780441013593",
            publication_year=1965
        )
        print("Geçerli kitap başarıyla oluşturuldu:")
        print(valid_book.model_dump_json(indent=2))
    except ValidationError as e:
        print(e)

    print("\n--- Geçersiz bir kitap oluşturma denemesi ---")
    try:
        _ = PydanticBook(
            title="Invalid Book",
            author="Bad Author",
            isbn="123",  # Çok kısa
            publication_year=1300  # gt=1400 kuralına aykırı
        )
    except ValidationError as e:
        print("Doğrulama beklendiği gibi başarısız oldu:")
        print(e)

    # Open Library ISBN örneği (interaktif değil; fonksiyon testlerle doğrulanıyor)


if __name__ == "__main__":
    main()


def fetch_book_details_by_isbn(isbn: str) -> tuple[str, str] | None:
    """Fetch book title and author(s) from Open Library by ISBN.

    Returns a tuple of (title, authors_string) if found; otherwise None.
    It never raises on network or parsing issues; instead returns None.
    """
    if not isbn or not isbn.strip():
        return None

    url = "https://openlibrary.org/api/books"
    params = {"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return None

    if not isinstance(payload, dict):
        return None

    key = f"ISBN:{isbn}"
    entry = payload.get(key)
    if not isinstance(entry, dict):
        return None

    title = entry.get("title")
    authors_list = entry.get("authors") or []
    author_names = ", ".join(
        [a.get("name", "").strip() for a in authors_list if isinstance(a, dict) and a.get("name")]
    )

    if not title or not author_names:
        return None

    return title, author_names


