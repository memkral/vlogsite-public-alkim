from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q
from .models import Vlog, Category, Comment
import re
import difflib


class VlogListView(ListView):
    model = Vlog
    template_name = 'vlogs/index.html'
    context_object_name = 'vlogs'
    paginate_by = 9

    def get_queryset(self):
        queryset = Vlog.objects.filter(is_published=True)
        query = self.request.GET.get('q', '').strip()
        cat = self.request.GET.get('cat', '').strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        if cat:
            queryset = queryset.filter(category__slug=cat)
        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '').strip()
        ctx['cat'] = self.request.GET.get('cat', '').strip()
        ctx['categories'] = Category.objects.all()
        # Öneriler: sonuç yoksa ve sorgu uygunsa benzer kelimeleri öner
        q = ctx['q']
        object_list = ctx.get('vlogs') or []
        if q and len(object_list) == 0 and self._query_is_suggestable(q):
            ctx['suggestions'] = self._generate_suggestions(q)
        else:
            ctx['suggestions'] = []
        return ctx

    # Yardımcılar
    def _query_is_suggestable(self, q: str) -> bool:
        if not (3 <= len(q) <= 40):
            return False
        # Harf/rakam oranı kontrolü (çok saçma girdileri ele)
        letters_digits = len(re.findall(r"[\wğüşöçıİĞÜŞÖÇ]", q, re.IGNORECASE))
        ratio = letters_digits / max(len(q), 1)
        return ratio >= 0.6

    def _generate_suggestions(self, q: str):
        # Sözlük: kategori ad/slug + başlıklardaki kelimeler
        vocab = set()
        for c in Category.objects.all():
            vocab.add(c.name.lower())
            vocab.add(str(c.slug).lower())
        for v in Vlog.objects.all():
            for token in re.findall(r"[\wğüşöçıİĞÜŞÖÇ]+", v.title.lower()):
                if len(token) >= 3:
                    vocab.add(token)
        # Çok kelimeli sorgu için kelime bazlı düzeltme
        words = [w for w in re.findall(r"[\wğüşöçıİĞÜŞÖÇ]+", q.lower()) if len(w) >= 3]
        corrected = []
        for w in words:
            match = difflib.get_close_matches(w, list(vocab), n=1, cutoff=0.7)
            corrected.append(match[0] if match else w)
        joined = " ".join(corrected).strip()
        candidates = set()
        if joined and joined != q.lower():
            candidates.add(joined)
        # Tek parça öneriler (örn. bir kategori adı)
        for m in difflib.get_close_matches(q.lower(), list(vocab), n=3, cutoff=0.7):
            candidates.add(m)
        # Başlıklara yakın tam öneri (örn. en yakın vlog başlığı)
        best_title = None
        best_ratio = 0.0
        for v in Vlog.objects.all():
            r = difflib.SequenceMatcher(None, q.lower(), v.title.lower()).ratio()
            if r > best_ratio:
                best_ratio = r
                best_title = v.title
        if best_title and best_ratio >= 0.6:
            candidates.add(best_title)
        # 3 öneri ile sınırla
        out = []
        for s in candidates:
            if len(out) >= 3:
                break
            out.append(s)
        return out


class VlogDetailView(DetailView):
    model = Vlog
    template_name = 'vlogs/detail.html'
    context_object_name = 'vlog'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        current: Vlog = ctx['vlog']
        ctx['related_vlogs'] = self.get_related_vlogs(current)
        ctx['comments'] = current.comments.filter(is_approved=True)
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        name = (request.POST.get('name') or '').strip()
        content = (request.POST.get('content') or '').strip()
        if name and content:
            Comment.objects.create(vlog=self.object, name=name, content=content, is_approved=True)
        # PRG deseni: yenilemede yeniden gönderimi önlemek için redirect
        from django.shortcuts import redirect
        return redirect(self.object.get_absolute_url())

    def get_related_vlogs(self, current: Vlog):
        # Basit benzerlik: kategori eşleşmesi + başlık ortak kelimeler
        base_qs = Vlog.objects.filter(is_published=True).exclude(id=current.id)
        scored = []
        current_tokens = set(re.findall(r"[\wğüşöçıİĞÜŞÖÇ]+", current.title.lower()))
        for v in base_qs:
            score = 0
            if current.category_id and v.category_id == current.category_id:
                score += 2
            vt = set(re.findall(r"[\wğüşöçıİĞÜŞÖÇ]+", v.title.lower()))
            score += len(current_tokens.intersection(vt))
            if score > 0:
                scored.append((score, v))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [v for _, v in scored[:6]]


class AboutView(TemplateView):
    template_name = 'pages/about.html'
