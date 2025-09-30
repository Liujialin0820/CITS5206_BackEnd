from rest_framework.routers import DefaultRouter
from students.views import StudentViewSet, StudentAttemptsAPI
from django.urls import path

router = DefaultRouter()
router.register(r"", StudentViewSet, basename="student")

urlpatterns = [
    # 其他 URL ...
    *router.urls,
    path(
        "<uuid:student_id>/attempts/", StudentAttemptsAPI.as_view()
    ),  # GET /students/<id>/attempts/
]
 