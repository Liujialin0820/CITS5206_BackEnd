from django.urls import path, include
from django.conf import settings

from django.conf.urls.static import static


urlpatterns = [
    path("user/", include("user.urls")),
    path("questions/", include("questions.urls")),
    path("test-papers/", include("testpaper.urls")),
    path("exam/", include("exam.urls")),  

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
