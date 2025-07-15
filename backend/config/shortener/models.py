from django.db import models
from django.utils import timezone
import string, random

class ShortURL(models.Model):
    url = models.URLField()
    shortcode = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry = models.DateTimeField()
    click_count = models.IntegerField(default=0)

    def __str__(self):
        return self.shortcode

    def is_expired(self):
        return timezone.now() > self.expiry

    def generate_shortcode(self):
        while True:
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            if not ShortURL.objects.filter(shortcode=code).exists():
                self.shortcode = code
                break

class Click(models.Model):
    shorturl = models.ForeignKey(ShortURL, on_delete=models.CASCADE, related_name='clicks')
    timestamp = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
