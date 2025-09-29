# testpaper/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestPaperViewSet

router = DefaultRouter()
router.register(r"", TestPaperViewSet, basename="testpapers")

urlpatterns = [
    path("", include(router.urls)),
]
