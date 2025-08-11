from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status

from .serializers import LoginSerializer, LimitedUserSerializer
from user_auth.authentications import generate_jwt_token

# Create your views here.


class login_view(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token = generate_jwt_token(user.uid)
            return Response({"token": token, "user": LimitedUserSerializer(user).data})
        else:
            detail = list(serializer.errors.values())[0][0]
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)


