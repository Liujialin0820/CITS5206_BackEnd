from rest_framework import serializers
from .models import Student
from exam.models import Attempt
from django.db.models import F   # ← 这里要导入
from testpaper.models import TestPaper

class StudentExamStatSerializer(serializers.ModelSerializer):
    attempts = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ["id", "student_no", "name", "email", "created_at", "attempts"]

    def get_attempts(self, obj):
        # 每个 level 的统计
        levels = ["Level 1", "Level 2", "Level 3", "Level 4"]
        stats = {}
        for lvl in levels:
            qs = Attempt.objects.filter(student=obj, paper__level=lvl)
            stats[lvl] = {
                "count": qs.count(),
                "passed": qs.filter(score__gte=F("total_marks") * 0.6).exists(),  # 60% 为及格
            }
        return stats

class PaperSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestPaper
        fields = ["id", "title", "level"]
        
class AttemptSerializer(serializers.ModelSerializer):
    paper = PaperSimpleSerializer(read_only=True)

    class Meta:
        model = Attempt
        fields = [
            "id",
            "paper",
            "score",
            "total_marks",
            "started_at",
            "submitted_at",
            "duration_seconds",
        ]


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "id",
            "student_no",
            "name",
            "email",
            "created_at",
        ]
