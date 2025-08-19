## Python OOP Kütüphane Sistemi

Basit bir kütüphane yönetim sistemi. OOP prensipleri (kalıtım, kapsülleme, polimorfizm, kompozisyon), birim testleri ve Open Library API ile ISBN'den kitap bilgisi çekme içerir. Terminal tabanlı bir menü ile kitap ekleme/silme/listeleme/arama yapılır. Kitaplar JSON dosyasında saklanır.

### Özellikler
- OOP sınıfları: `Book`, `EBook`, `AudioBook`, `Library`, `Member`
- Open Library API ile ISBN'den başlık ve yazar(lar) çekme
- Terminal menüsü (`main.py`): kitap ekle/sil/listele/ara
- JSON kalıcılık: `library_data.json`
- Testler: `pytest`

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

### Testleri Çalıştırma
```bash
pytest -q
```

## API (Aşama 3 - İsteğe Bağlı)
Bu repo, minimum gereksinimleri (Aşama 1-2) karşılayacak şekilde teslim edilmiştir. API (Aşama 3) henüz eklenmedi. İstenirse aşağıdaki örnek çalışma şekli hedeflenir:
- Sunucu başlatma: `uvicorn api:app --reload`
- Örnek endpointler:
  - `GET /books` — Kayıtlı kitapları döndürür
  - `POST /books` — Body: `{ "isbn": "..." }` (Open Library ile başlık/yazar çekip kaydedebilir)
  - `DELETE /books/{isbn}` — ISBN ile siler

## Proje Yapısı
```
library.py       # OOP sınıfları + Open Library yardımcı fonksiyonu + (demo fonksiyonu)
main.py          # Terminal menüsü ve JSON kalıcılık
test_library.py  # Pytest birim testleri
requirements.txt # Bağımlılıklar (pydantic, pytest, requests)
```

## Notlar
- `library_data.json` çalışma sırasında oluşturulur ve kitapları saklar.
- Open Library isteği başarısız/sonuçsuz olursa uygulama çökmeyecek şekilde tasarlanmıştır.


