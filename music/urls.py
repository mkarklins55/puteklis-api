from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import HealthView, SongViewSet


router = DefaultRouter()
router.register('songs', SongViewSet, basename='song')

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
]
urlpatterns += router.urls
