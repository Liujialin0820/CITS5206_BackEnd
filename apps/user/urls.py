from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

app_name = "user"

router = DefaultRouter()

urlpatterns = [
    path("login/", views.login_view.as_view(), name="login"),
] + router.urls
