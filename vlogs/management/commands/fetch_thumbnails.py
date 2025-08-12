import io
import os
import re
import requests
from PIL import Image, ImageDraw, ImageFont
from urllib.parse import urlparse, parse_qs
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.conf import settings
from vlogs.models import Vlog


class Command(BaseCommand):
    help = "Eksik thumbnail'leri video URL'sinden çek veya başlığa göre placeholder üret"

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Var olanı da güncelle')

    def handle(self, *args, **options):
        force = options.get('force', False)
        updated = 0
        for vlog in Vlog.objects.all():
            if vlog.thumbnail and not force:
                continue
            content = self.fetch_thumbnail_content(vlog) or self.generate_placeholder(vlog.title)
            if not content:
                continue
            filename = f"thumb_{vlog.slug}.jpg"
            vlog.thumbnail.save(filename, ContentFile(content), save=True)
            updated += 1
            self.stdout.write(self.style.SUCCESS(f"✓ {vlog.title}: thumbnail atandi"))
        self.stdout.write(self.style.NOTICE(f"Toplam guncellenen: {updated}"))

    # ---- helpers ----
    def fetch_thumbnail_content(self, vlog):
        url = str(vlog.video_url)
        try:
            # YouTube ID'den hızlı çekim
            yt = self.extract_youtube_id(url)
            if yt:
                for quality in ["maxresdefault", "sddefault", "hqdefault", "mqdefault"]:
                    thumb_url = f"https://img.youtube.com/vi/{yt}/{quality}.jpg"
                    content = self.http_get_bytes(thumb_url)
                    if content:
                        return content
            # OpenGraph og:image dene
            html = self.http_get_text(url, timeout=5)
            if html:
                m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
                if m:
                    content = self.http_get_bytes(m.group(1))
                    if content:
                        return content
        except Exception:
            return None
        return None

    def extract_youtube_id(self, url: str):
        try:
            u = urlparse(url)
            if 'youtube.com' in u.netloc:
                q = parse_qs(u.query)
                return (q.get('v') or [None])[0]
            if 'youtu.be' in u.netloc:
                return u.path.strip('/')
        except Exception:
            return None
        return None

    def http_get_bytes(self, url: str, timeout: int = 8):
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200 and r.content:
                return r.content
        except Exception:
            return None
        return None

    def http_get_text(self, url: str, timeout: int = 6):
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200 and r.text:
                return r.text
        except Exception:
            return None
        return None

    def generate_placeholder(self, title: str) -> bytes | None:
        try:
            width, height = 1280, 720
            img = Image.new('RGB', (width, height), color=(18, 18, 18))
            draw = ImageDraw.Draw(img)
            # Gradient vurgular
            for i in range(0, 260):
                draw.line([(0, i*3), (width, i*3)], fill=(12 + i//3, 12, 24), width=3)
            # Başlık
            text = (title or 'Vlog').strip()
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 64)
            except Exception:
                font = ImageFont.load_default()
            text = (text[:60] + '…') if len(text) > 60 else text
            tw, th = draw.textbbox((0, 0), text, font=font)[2:]
            x = (width - tw) // 2
            y = (height - th) // 2
            draw.text((x, y), text, fill=(230, 230, 230), font=font)
            # Kaydet
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=85)
            return buf.getvalue()
        except Exception:
            return None


