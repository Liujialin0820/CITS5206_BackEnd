# testpaper/serializers.py
from rest_framework import serializers
from .models import TestPaper
from questions.serializers import QuestionSerializer


class TestPaperSerializer(serializers.ModelSerializer):
    # 显示关联的题目（只读）
    questions_detail = QuestionSerializer(source="questions", many=True, read_only=True)

    class Meta:
        model = TestPaper
        fields = [
            "id",
            "title",
            "level",
            "category",
            "status",
            "questions",  # 写入时传 ID 列表
            "questions_detail",  # 返回时带题目详情
            "created_at",
            "level_config",  # ✅ 新增字段
        ]
