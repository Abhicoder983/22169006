from django.urls import path
from .views import CreateShortURL, RetrieveShortURLStats, RedirectShortURL

urlpatterns = [
    path('shorturls', CreateShortURL.as_view()),
    path('shorturls/<str:shortcode>', RetrieveShortURLStats.as_view()),
    path('<str:shortcode>', RedirectShortURL.as_view()),
]
