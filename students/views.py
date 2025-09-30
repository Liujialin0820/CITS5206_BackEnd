from rest_framework import viewsets
from .models import Student
from .serializers import StudentExamStatSerializer
# students/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Student
from exam.models import Attempt
from .serializers import StudentSerializer,AttemptSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().order_by("-created_at")
    serializer_class = StudentExamStatSerializer



class StudentAttemptsAPI(APIView):
    def get(self, request, student_id):
        qs = Attempt.objects.filter(student_id=student_id).select_related("paper")
        data = AttemptSerializer(qs, many=True).data
        return Response({"attempts_detail": data}, status=status.HTTP_200_OK)