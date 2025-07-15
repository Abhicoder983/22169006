# shortener/views.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import ShortenedURL
from .serializers import ShortenedURLSerializer, URLStatsSerializer
from .services import URLShortenerService
import logging

logger = logging.getLogger(__name__)

class CreateShortURLView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            logger.info("Received request to create short URL")
            
            original_url = request.data.get('url')
            validity = request.data.get('validity', 30)
            short_code = request.data.get('shortcode')
            
            if not original_url:
                logger.error("Original URL is required")
                return Response(
                    {"error": "Original URL is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                short_url = URLShortenerService.create_short_url(
                    original_url=original_url,
                    validity=validity,
                    short_code=short_code
                )
                
                serializer = ShortenedURLSerializer(
                    short_url,
                    context={'request': request, 'validity': validity}
                )
                
                logger.info("Successfully created short URL")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
            except ValueError as e:
                logger.error(f"Validation error: {str(e)}")
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RedirectShortURLView(APIView):
    def get(self, request, short_code):
        try:
            logger.info(f"Received request to redirect short URL: {short_code}")
            
            original_url = URLShortenerService.get_original_url(short_code)
            short_url = ShortenedURL.objects.get(short_code=short_code)
            
            # Log the access
            URLShortenerService.log_access(short_url, request)
            
            logger.info(f"Redirecting to original URL: {original_url}")
            return Response(
                {"Location": original_url},
                status=status.HTTP_302_FOUND,
                headers={"Location": original_url}
            )
            
        except ValueError as e:
            logger.error(f"Error redirecting: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() 
                else status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class URLStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, short_code):
        try:
            logger.info(f"Received request for stats of short URL: {short_code}")
            
            short_url = URLShortenerService.get_url_stats(short_code)
            serializer = URLStatsSerializer(short_url)
            
            logger.info("Successfully retrieved URL stats")
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.error(f"Error getting stats: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() 
                else status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )