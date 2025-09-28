# students/views.py
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from .models import Student
from .serializers import StudentSerializer


class StudentPagination(PageNumberPagination):
    page_size = 6  # 默认每页 6 条
    page_size_query_param = "page_size"
    max_page_size = 100


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    pagination_class = StudentPagination
