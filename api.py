"""
FastAPI Web API for Library Management System
Aşama 3: FastAPI ile Kendi API'nizi Oluşturma
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from library import Library, Book, fetch_book_details_by_isbn
import json
import os

app = FastAPI(
    title="Library Management API",
    description="A REST API for managing books in a library system",
    version="1.0.0"
)

# Global library instance with persistence
DATA_FILE = "api_library_data.json"
library = Library.load_from_file(DATA_FILE, default_name="API Library")

# Pydantic models for request/response validation
class BookResponse(BaseModel):
    title: str
    author: str
    isbn: str
    is_borrowed: bool
    book_type: str = "Book"
    file_format: str | None = None
    duration: int | None = None

class ISBNRequest(BaseModel):
    isbn: str

class MessageResponse(BaseModel):
    message: str
    success: bool

# Helper function to convert Book objects to BookResponse
def book_to_response(book: Book) -> BookResponse:
    book_type = book.__class__.__name__
    return BookResponse(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        is_borrowed=book.is_borrowed,
        book_type=book_type,
        file_format=getattr(book, 'file_format', None),
        duration=getattr(book, 'duration', None)
    )

# API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Library Management API",
        "docs": "/docs",
        "total_books": str(library.total_books)
    }

@app.get("/books", response_model=List[BookResponse])
async def get_books():
    """GET /books: Kütüphanedeki tüm kitapların listesini JSON olarak döndürür."""
    books = library.list_books()
    return [book_to_response(book) for book in books]

@app.post("/books", response_model=BookResponse)
async def add_book(isbn_request: ISBNRequest):
    """
    POST /books: Request body'sinde bir ISBN alır, Open Library'den verileri çeker 
    ve kitabı kütüphaneye ekler.
    """
    isbn = isbn_request.isbn.strip()
    
    if not isbn:
        raise HTTPException(status_code=400, detail="ISBN cannot be empty")
    
    # Check if book already exists
    existing_book = library.find_book_by_isbn(isbn)
    if existing_book:
        raise HTTPException(
            status_code=409, 
            detail=f"Book with ISBN {isbn} already exists in library"
        )
    
    # Fetch book details from Open Library
    book_details = fetch_book_details_by_isbn(isbn)
    if not book_details:
        raise HTTPException(
            status_code=404,
            detail=f"Book with ISBN {isbn} not found in Open Library"
        )
    
    title, authors = book_details
    
    # Create and add the book
    new_book = Book(title=title, author=authors, isbn=isbn)
    library.add_book(new_book)
    
    # Save to file
    library.save_to_file(DATA_FILE)
    
    return book_to_response(new_book)

@app.delete("/books/{isbn}", response_model=MessageResponse)
async def delete_book(isbn: str):
    """DELETE /books/{isbn}: Belirtilen ISBN'e sahip kitabı kütüphaneden siler."""
    isbn = isbn.strip()
    
    if not isbn:
        raise HTTPException(status_code=400, detail="ISBN cannot be empty")
    
    # Try to remove the book
    success = library.remove_book_by_isbn(isbn)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Book with ISBN {isbn} not found in library"
        )
    
    # Save to file
    library.save_to_file(DATA_FILE)
    
    return MessageResponse(
        message=f"Book with ISBN {isbn} successfully removed",
        success=True
    )

@app.get("/books/{isbn}", response_model=BookResponse)
async def get_book_by_isbn(isbn: str):
    """GET /books/{isbn}: Belirtilen ISBN'e sahip kitabı döndürür."""
    isbn = isbn.strip()
    
    if not isbn:
        raise HTTPException(status_code=400, detail="ISBN cannot be empty")
    
    book = library.find_book_by_isbn(isbn)
    if not book:
        raise HTTPException(
            status_code=404,
            detail=f"Book with ISBN {isbn} not found in library"
        )
    
    return book_to_response(book)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "library_name": library.name}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
