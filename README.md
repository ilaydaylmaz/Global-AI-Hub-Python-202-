## Python OOP Kütüphane Sistemi

Tam kapsamlı bir kütüphane yönetim sistemi. OOP prensipleri (kalıtım, kapsülleme, polimorfizm, kompozisyon), birim testleri, Open Library API entegrasyonu ve FastAPI web servisi içerir. Hem terminal tabanlı menü hem de REST API ile kitap yönetimi yapılabilir. Kitaplar JSON dosyasında saklanır.

### Özellikler
- **OOP sınıfları**: `Book`, `EBook`, `AudioBook`, `Library`, `Member`
- **Open Library API** ile ISBN'den başlık ve yazar(lar) çekme
- **Terminal menüsü** (`main.py`): kitap ekle/sil/listele/ara
- **FastAPI web servisi** (`api.py`): REST API endpoints
- **JSON kalıcılık**: `library_data.json` ve `api_library_data.json`
- **Kapsamlı testler**: `pytest` ile birim ve API testleri

## Kurulum
```bash
git clone <SIZIN_REPO_URLINIZ>
cd python_oop_kutuphane
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Kullanım
### Terminal Uygulaması (Aşama 1-2)
```bash
python main.py
```
- 1: Kitap Ekle (ISBN ile otomatik doldurma desteklenir; API bulunamazsa manuel girişe düşer)
- 2: Kitap Sil (ISBN ile)
- 3: Kitapları Listele
- 4: Kitap Ara (başlığa göre)
- 5: Çıkış (değişiklikler otomatik kaydedilir)

### FastAPI Web Servisi (Aşama 3)
```bash
uvicorn api:app --reload
```
- API sunucusu `http://localhost:8000` adresinde çalışır
- Otomatik dokümantasyon: `http://localhost:8000/docs`
- Alternatif dokümantasyon: `http://localhost:8000/redoc`

### Testleri Çalıştırma
```bash
# Tüm testleri çalıştır (birim + API testleri)
pytest -v

# Sadece birim testleri
pytest test_library.py -v

# Sadece API testleri
pytest test_api.py -v
```

## API Dokümantasyonu (Aşama 3)

### Endpoints

#### `GET /books`
Kütüphanedeki tüm kitapların listesini döndürür.

**Response:**
```json
[
  {
    "title": "Book Title",
    "author": "Author Name",
    "isbn": "9780123456789",
    "is_borrowed": false,
    "book_type": "Book",
    "file_format": null,
    "duration": null
  }
]
```

#### `POST /books`
ISBN ile Open Library'den kitap bilgilerini çekerek kütüphaneye ekler.

**Request Body:**
```json
{
  "isbn": "9780140328721"
}
```

**Response (Success):**
```json
{
  "title": "Fantastic Mr. Fox",
  "author": "Roald Dahl",
  "isbn": "9780140328721",
  "is_borrowed": false,
  "book_type": "Book",
  "file_format": null,
  "duration": null
}
```

**Response (Error 404):**
```json
{
  "detail": "Book with ISBN 9780140328721 not found in Open Library"
}
```

**Response (Error 409):**
```json
{
  "detail": "Book with ISBN 9780140328721 already exists in library"
}
```

#### `GET /books/{isbn}`
Belirtilen ISBN'e sahip kitabın bilgilerini döndürür.

**Response:**
```json
{
  "title": "Book Title",
  "author": "Author Name",
  "isbn": "9780123456789",
  "is_borrowed": false,
  "book_type": "Book",
  "file_format": null,
  "duration": null
}
```

#### `DELETE /books/{isbn}`
Belirtilen ISBN'e sahip kitabı kütüphaneden siler.

**Response:**
```json
{
  "message": "Book with ISBN 9780123456789 successfully removed",
  "success": true
}
```

#### `GET /health`
API sağlık kontrolü.

**Response:**
```json
{
  "status": "healthy",
  "library_name": "API Library"
}
```

## Proje Yapısı
```
library.py         # OOP sınıfları + Open Library yardımcı fonksiyonu
main.py            # Terminal menüsü ve JSON kalıcılık
api.py             # FastAPI web servisi ve REST API endpoints
test_library.py    # Birim testleri (OOP sınıfları)
test_api.py        # API testleri (FastAPI endpoints)
requirements.txt   # Bağımlılıklar (pydantic, pytest, requests, fastapi, uvicorn)
README.md          # Bu dosya
.gitignore         # Git ignore kuralları
```

## Notlar
- **Terminal uygulaması**: `library_data.json` dosyasını kullanır
- **API servisi**: `api_library_data.json` dosyasını kullanır (ayrı veri)
- Open Library isteği başarısız/sonuçsuz olursa uygulama çökmeyecek şekilde tasarlanmıştır
- API otomatik dokümantasyon `/docs` endpoint'inde mevcuttur
- Tüm endpoints Pydantic ile validasyon yapar


