from rest_framework import viewsets
from .models import Question
from .serializers import QuestionReadSerializer, QuestionWriteSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all().order_by("-created_at")

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return QuestionWriteSerializer
        return QuestionReadSerializer
