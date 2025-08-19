from library import Library, Book, fetch_book_details_by_isbn

DATA_FILE = "library_data.json"


def prompt_non_empty(prompt_text: str) -> str:
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("Boş bırakılamaz. Lütfen tekrar deneyin.")


def add_book_flow(lib: Library) -> None:
    print("\n=== Kitap Ekle ===")
    choice = input("ISBN ile otomatik doldur? (E/h): ").strip().lower()
    if choice == "e":
        isbn = prompt_non_empty("ISBN: ")
        details = fetch_book_details_by_isbn(isbn)
        if details:
            title, authors = details
            print(f"Bulundu: {title} - {authors}")
            lib.add_book(Book(title=title, author=authors, isbn=isbn))
            print("Kitap eklendi.")
            return
        else:
            print("Open Library'de bulunamadı. Elle girişe geçiliyor.")

    title = prompt_non_empty("Başlık: ")
    author = prompt_non_empty("Yazar: ")
    isbn = prompt_non_empty("ISBN: ")
    lib.add_book(Book(title=title, author=author, isbn=isbn))
    print("Kitap eklendi.")


def remove_book_flow(lib: Library) -> None:
    print("\n=== Kitap Sil ===")
    isbn = prompt_non_empty("Silinecek kitabın ISBN'i: ")
    ok = lib.remove_book_by_isbn(isbn)
    if ok:
        print("Kitap silindi.")
    else:
        print("ISBN bulunamadı.")


def list_books_flow(lib: Library) -> None:
    print("\n=== Kitapları Listele ===")
    books = lib.list_books()
    if not books:
        print("Kütüphanede kitap yok.")
        return
    for idx, b in enumerate(books, start=1):
        print(f"{idx}. {b.display_info()} [ISBN: {b.isbn}] {'(Ödünçte)' if b.is_borrowed else ''}")


def search_book_flow(lib: Library) -> None:
    print("\n=== Kitap Ara ===")
    query = prompt_non_empty("Başlık: ")
    book = lib.find_book(query)
    if book:
        print(f"Bulundu: {book.display_info()} [ISBN: {book.isbn}]")
    else:
        print("Kitap bulunamadı.")


def main() -> None:
    lib = Library.load_from_file(DATA_FILE, default_name="My Library")
    while True:
        print("\n=== Menü ===")
        print("1. Kitap Ekle")
        print("2. Kitap Sil")
        print("3. Kitapları Listele")
        print("4. Kitap Ara")
        print("5. Çıkış")
        choice = input("Seçiminiz: ").strip()

        if choice == "1":
            add_book_flow(lib)
            lib.save_to_file(DATA_FILE)
        elif choice == "2":
            remove_book_flow(lib)
            lib.save_to_file(DATA_FILE)
        elif choice == "3":
            list_books_flow(lib)
        elif choice == "4":
            search_book_flow(lib)
        elif choice == "5":
            print("Güle güle!")
            lib.save_to_file(DATA_FILE)
            break
        else:
            print("Geçersiz seçim. Lütfen 1-5 arası bir değer girin.")


if __name__ == "__main__":
    main()


