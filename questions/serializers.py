import json
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


class QuestionSerializer(serializers.ModelSerializer):
    # 用于返回时嵌套
    choices = ChoiceSerializer(many=True, read_only=True)
    image = QuestionImageSerializer(read_only=True)

    # 用于写入时接收 JSON 字符串
    choices_json = serializers.CharField(write_only=True, required=True)

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
            "choices",      # 返回时显示
            "choices_json", # 写入时用
            "image",
        ]

    def create(self, validated_data):
        # 处理 choices_json
        choices_raw = validated_data.pop("choices_json")
        try:
            choices_data = json.loads(choices_raw)
        except Exception:
            raise serializers.ValidationError({"choices": "Invalid JSON format"})

        request = self.context.get("request")
        question = Question.objects.create(**validated_data)

        # 保存 choices
        for choice in choices_data:
            Choice.objects.create(question=question, **choice)

        # 保存单图
        if request and "image" in request.FILES:
            QuestionImage.objects.create(question=question, image=request.FILES["image"])

        return question

    def update(self, instance, validated_data):
        choices_raw = validated_data.pop("choices_json", None)
        request = self.context.get("request")

        # 更新基础字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 更新 choices
        if choices_raw:
            try:
                choices_data = json.loads(choices_raw)
            except Exception:
                raise serializers.ValidationError({"choices": "Invalid JSON format"})

            instance.choices.all().delete()
            for choice in choices_data:
                Choice.objects.create(question=instance, **choice)

        # 更新 image
        if request and "image" in request.FILES:
            if hasattr(instance, "image"):
                instance.image.delete()
            QuestionImage.objects.update_or_create(
                question=instance, defaults={"image": request.FILES["image"]}
            )

        return instance


class ChoicePreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text"]   # ❌ 不要返回 is_correct

class QuestionPreviewSerializer(serializers.ModelSerializer):
    choices = ChoicePreviewSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "question_text", "type", "marks", "choices"]