from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import HealthView, MetricsView, SongViewSet

router = DefaultRouter()
router.register("songs", SongViewSet, basename="song")

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("metrics/", MetricsView.as_view(), name="metrics"),
]
urlpatterns += router.urls
