

import logging
from django.utils import timezone
from .models import ShortenedURL, URLAccessLog

logger = logging.getLogger(__name__)

class URLShortenerService:
    @staticmethod
    def create_short_url(original_url, validity=30, short_code=None):
        try:
            if not original_url:
                logger.error("Original URL is required")
                raise ValueError("Original URL is required")
            
            if short_code and ShortenedURL.objects.filter(short_code=short_code).exists():
                logger.warning(f"Short code {short_code} already exists")
                raise ValueError("Short code already exists")
            
            if not short_code:
                short_code = ShortenedURL.generate_short_code()
                logger.info(f"Generated new short code: {short_code}")
            
            expires_at = timezone.now() + timezone.timedelta(minutes=validity)
            
            short_url = ShortenedURL.objects.create(
                original_url=original_url,
                short_code=short_code,
                expires_at=expires_at
            )
            
            logger.info(f"Created new short URL: {short_url.short_code}")
            return short_url
            
        except Exception as e:
            logger.error(f"Error creating short URL: {str(e)}")
            raise

    @staticmethod
    def get_original_url(short_code):
        try:
            short_url = ShortenedURL.objects.get(short_code=short_code, is_active=True)
            
            if timezone.now() > short_url.expires_at:
                logger.warning(f"Short URL {short_code} has expired")
                short_url.is_active = False
                short_url.save()
                raise ValueError("Short URL has expired")
                
            return short_url.original_url
            
        except ShortenedURL.DoesNotExist:
            logger.warning(f"Short URL {short_code} not found")
            raise ValueError("Short URL not found")
        except Exception as e:
            logger.error(f"Error retrieving original URL: {str(e)}")
            raise

    @staticmethod
    def log_access(short_url, request):
        try:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            
            referrer = request.META.get('HTTP_REFERER')
            user_agent = request.META.get('HTTP_USER_AGENT')
            
            # In a real implementation, you would use a geoip service here
            country = "Unknown"
            city = "Unknown"
            
            URLAccessLog.objects.create(
                shortened_url=short_url,
                ip_address=ip_address,
                referrer=referrer,
                user_agent=user_agent,
                country=country,
                city=city
            )
            
            logger.info(f"Logged access to {short_url.short_code} from {ip_address}")
            
        except Exception as e:
            logger.error(f"Error logging access: {str(e)}")
            raise

    @staticmethod
    def get_url_stats(short_code):
        try:
            short_url = ShortenedURL.objects.get(short_code=short_code)
            return short_url
            
        except ShortenedURL.DoesNotExist:
            logger.warning(f"Short URL {short_code} not found for stats")
            raise ValueError("Short URL not found")
        except Exception as e:
            logger.error(f"Error retrieving URL stats: {str(e)}")
            raise