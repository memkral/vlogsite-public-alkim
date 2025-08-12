# VlogSite (Django 5)

Koyu temalı modern bir Django vlog platformu. YouTube/Vimeo gömme, arama, kategori filtresi, öneriler, yorumlar ve otomatik thumbnail üretimi içerir.

## Hızlı Başlangıç
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata fixtures/users.json fixtures/vlogs.json
python manage.py runserver
# (Opsiyonel) Thumbnail üretimi/yenileme
python manage.py fetch_thumbnails --force
```

## Özellikler
- Koyu tema (Bootstrap 5 + özel CSS)
- Vlog listesi ve detay sayfası
- Arama (`q`) ve kategori filtresi (`cat`)
- Sonuç yokken akıllı öneriler (“Bunu mu demek istediniz?”)
- İlgili vloglar (basit benzerlik skoru)
- Yorumlar (PRG pattern, 100 örnek yorum seed)
- Otomatik thumbnail komutu: `fetch_thumbnails`

## Fixture’lar
- `fixtures/users.json`: admin kullanıcısı
- `fixtures/vlogs.json`: kategoriler, vloglar ve yorumlar

## Lisans
MIT
