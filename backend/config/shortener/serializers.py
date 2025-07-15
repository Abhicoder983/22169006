

from rest_framework import serializers
from .models import ShortenedURL, URLAccessLog
from django.utils import timezone
from datetime import timedelta

class ShortenedURLSerializer(serializers.ModelSerializer):
    short_url = serializers.SerializerMethodField()
    expires_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    
    class Meta:
        model = ShortenedURL
        fields = ['short_url', 'original_url', 'short_code', 'expires_at']
        extra_kwargs = {
            'original_url': {'write_only': True},
            'short_code': {'required': False},
        }
    
    def get_short_url(self, obj):
        request = self.context.get('request')
        base_url = request.build_absolute_uri('/') if request else ''
        return f"{base_url}{obj.short_code}"
    
    def validate_short_code(self, value):
        if value and not value.isalnum():
            raise serializers.ValidationError("Short code must be alphanumeric.")
        return value
    
    def create(self, validated_data):
        original_url = validated_data['original_url']
        short_code = validated_data.get('short_code')
        validity = self.context.get('validity', 30)  # Default 30 minutes
        
        if not short_code:
            short_code = ShortenedURL.generate_short_code()
        
        expires_at = timezone.now() + timedelta(minutes=validity)
        
        return ShortenedURL.objects.create(
            original_url=original_url,
            short_code=short_code,
            expires_at=expires_at
        )

class URLAccessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = URLAccessLog
        fields = ['accessed_at', 'referrer', 'country', 'city']

class URLStatsSerializer(serializers.ModelSerializer):
    access_count = serializers.SerializerMethodField()
    access_logs = URLAccessLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = ShortenedURL
        fields = ['original_url', 'short_code', 'created_at', 'expires_at', 
                 'access_count', 'access_logs']
    
    def get_access_count(self, obj):
        return obj.access_logs.count()