from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from .models import ShortURL, Click
from .serializers import ShortURLSerializer

class CreateShortURL(APIView):
    def post(self, request):
        serializer = ShortURLSerializer(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data['url']
            validity = serializer.validated_data.get('validity', 30)
            shortcode = serializer.validated_data.get('shortcode')

            expiry = timezone.now() + timezone.timedelta(minutes=validity)
            if shortcode:
                if ShortURL.objects.filter(shortcode=shortcode).exists():
                    return Response({'error': 'Shortcode already exists'}, status=400)
            else:
                shortcode = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
                while ShortURL.objects.filter(shortcode=shortcode).exists():
                    shortcode = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

            shorturl = ShortURL.objects.create(url=url, shortcode=shortcode, expiry=expiry)
            return Response({
                'shortLink': f"http://localhost:8000/{shortcode}",
                'expiry': shorturl.expiry
            }, status=201)
        return Response(serializer.errors, status=400)

class RetrieveShortURLStats(APIView):
    def get(self, request, shortcode):
        shorturl = get_object_or_404(ShortURL, shortcode=shortcode)
        clicks = shorturl.clicks.all()
        click_list = [{
            'timestamp': c.timestamp,
            'source': c.source,
            'location': c.location
        } for c in clicks]

        return Response({
            'totalClicks': shorturl.click_count,
            'originalURL': shorturl.url,
            'creationDate': shorturl.created_at,
            'expiry': shorturl.expiry,
            'clicks': click_list
        })

class RedirectShortURL(APIView):
    def get(self, request, shortcode):
        shorturl = get_object_or_404(ShortURL, shortcode=shortcode)
        if shorturl.is_expired():
            return Response({'error': 'Link expired'}, status=410)

        shorturl.click_count += 1
        shorturl.save()
        Click.objects.create(shorturl=shorturl, source=request.META.get('HTTP_REFERER'), location='India')  # Simplified location

        return redirect(shorturl.url)
