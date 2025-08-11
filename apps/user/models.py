from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.contrib.auth.hashers import make_password
from shortuuidfield import ShortUUIDField
from django.utils import timezone

# Create your models here.
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, first_name, email, password, **extra_fields):
        if not first_name:
            raise ValueError("Must set real name!")
        email = self.normalize_email(email)
        user = self.model(first_name=first_name, email=email, **extra_fields)
        user.password = make_password(password)
        user.save()
        return user

    def create_student(self, first_name, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(first_name, email, password, **extra_fields)

    def create_superuser(self, first_name, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("super user must set is_superuser=True.")

        return self._create_user(first_name, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    uid = ShortUUIDField(primary_key=True)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True, blank=False)
    phone = models.CharField(max_length=20, blank=True)
    Enrolled = models.BooleanField(default=True)

    # don't use this field
    is_active = models.BooleanField(default=True)
    post_code = models.CharField(max_length=10, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    enrolled_until = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "password"]

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return self.first_name

    def get_short_name(self):
        return self.first_name

    class Meta:
        ordering = ("-date_joined",)
