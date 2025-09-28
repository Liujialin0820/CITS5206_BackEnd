from rest_framework import serializers
from .models import Question, Choice, QuestionImage


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text", "is_correct"]


class QuestionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionImage
        fields = ["id", "image"]


# Serializer for reading (nested choices + images)
class QuestionReadSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    images = QuestionImageSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "name",
            "type",
            "level",
            "category",
            "marks",
            "question_text",
            "choices",
            "images",
        ]


# Serializer for writing (choices as JSON + images in request.FILES)
class QuestionWriteSerializer(serializers.ModelSerializer):
    choices = serializers.JSONField(write_only=True, required=True)

    class Meta:
        model = Question
        fields = [
            "name",
            "type",
            "level",
            "category",
            "marks",
            "question_text",
            "choices",
            "images",  # dummy field to avoid "unknown field"
        ]

    def create(self, validated_data):
        choices_data = validated_data.pop("choices")
        validated_data.pop("images", None)  # remove dummy field

        # create question
        question = Question.objects.create(**validated_data)

        # create choices
        for choice in choices_data:
            Choice.objects.create(
                question=question,
                text=choice["text"],
                is_correct=choice["is_correct"],
            )

        # handle images
        request = self.context.get("request")
        if request and request.FILES:
            for f in request.FILES.getlist("images"):
                QuestionImage.objects.create(question=question, image=f)

        return question
