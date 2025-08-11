from rest_framework import serializers
from rest_framework import exceptions
from .models import User


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True, error_messages={"required": "Please enter your email address."}
    )
    password = serializers.CharField(min_length=4)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = User.objects.filter(email=email).first()
            if user and user.check_password(password):
                attrs["user"] = user
            else:
                msg = "Unable to log in with provided credentials."
                raise exceptions.ValidationError(msg)
        else:
            msg = "Must include 'username' and 'password'."
            raise exceptions.ValidationError(msg)
        return attrs
    

class LimitedUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = (
            "password",
            "is_superuser",
            "is_active",
            "groups",
            "user_permissions",
            "enrolled_until",
            "date_joined",
            "last_login",
        )
