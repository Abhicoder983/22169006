# shortener/models.py

from django.db import models
from django.utils import timezone
import uuid
import random
import string

class ShortenedURL(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"
    
    @classmethod
    def generate_short_code(cls, length=8):
        """Generate a random short code"""
        chars = string.ascii_letters + string.digits
        while True:
            short_code = ''.join(random.choice(chars) for _ in range(length))
            if not cls.objects.filter(short_code=short_code).exists():
                return short_code

class URLAccessLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shortened_url = models.ForeignKey(ShortenedURL, on_delete=models.CASCADE, related_name='access_logs')
    accessed_at = models.DateTimeField(auto_now_add=True)
    referrer = models.URLField(max_length=2048, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"Access to {self.shortened_url.short_code} at {self.accessed_at}"