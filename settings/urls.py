from django.urls import path, include
from django.conf import settings

from django.conf.urls.static import static


urlpatterns = [
    path("user/", include("user.urls")),
    path("questions/", include("questions.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
