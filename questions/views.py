from rest_framework import viewsets
import csv, io
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Question, Choice
from .serializers import QuestionSerializer
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend




class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    # ✅ 支持 search / filter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name", "question_text"]
    filterset_fields = ["category", "level"]


    @action(detail=False, methods=["post"])
    def import_csv(self, request):
        """
        Bulk import questions from CSV.
        Expected CSV header:
        name,type,level,category,marks,question,choices,correctIndex
        """
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = file.read().decode("utf-8")
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        questions_to_create = []
        choices_to_create = []

        for row in reader:
            q = Question(
                name=row["name"],
                type=row["type"],
                level=row["level"],
                category=row["category"],
                marks=int(row["marks"]),
                question_text=row["question"],
            )
            questions_to_create.append((q, row))

        # 批量创建 Question
        created_questions = Question.objects.bulk_create([q for q, _ in questions_to_create])

        # 批量创建 Choice
        for q, row in zip(created_questions, [r for _, r in questions_to_create]):
            choices = row["choices"].split("|")
            correct_indexes = [int(x) for x in row["correctIndex"].split(",")]
            for i, text in enumerate(choices):
                choices_to_create.append(
                    Choice(question=q, text=text.strip(), is_correct=i in correct_indexes)
                )

        Choice.objects.bulk_create(choices_to_create)

        return Response(
            {"message": f"Imported {len(created_questions)} questions"},
            status=status.HTTP_201_CREATED,
        )