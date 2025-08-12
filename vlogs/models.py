from django.db import models
from django.contrib.auth.models import User
from embed_video.fields import EmbedVideoField
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"

    def __str__(self) -> str:
        return self.name


class Vlog(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vlogs")
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True)
    description = models.TextField()
    video_url = EmbedVideoField(help_text="YouTube/Vimeo linki")
    thumbnail = models.ImageField(upload_to="thumbnails/", blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="vlogs")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Vlog"
        verbose_name_plural = "Vloglar"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse('vlogs:detail', args=[self.slug])


class Comment(models.Model):
    vlog = models.ForeignKey(Vlog, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=80)
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Yorum"
        verbose_name_plural = "Yorumlar"

    def __str__(self) -> str:
        return f"{self.name} - {self.vlog.title}"

# Create your models here.
