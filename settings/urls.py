from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path("user/", include("user.urls")),
]
