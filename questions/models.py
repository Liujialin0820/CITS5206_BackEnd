from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Question(models.Model):
    QUESTION_TYPES = [
        ("Multiple Choice", "Multiple Choice"),
        ("Single Choice", "Single Choice"),
    ]
    LEVELS = [
        ("Level 1", "Level 1"),
        ("Level 2", "Level 2"),
        ("Level 3", "Level 3"),
        ("Level 4", "Level 4"),
    ]
    CATEGORIES = [
        ("Vocabulary", "Vocabulary"),
        ("Grammar", "Grammar"),
    ]

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=QUESTION_TYPES)
    level = models.CharField(max_length=50, choices=LEVELS)
    category = models.CharField(max_length=100, choices=CATEGORIES)
    marks = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class Choice(models.Model):
    question = models.ForeignKey(
        Question, related_name="choices", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.text} ({'✔' if self.is_correct else '✘'})"


class QuestionImage(models.Model):
    question = models.ForeignKey(
        Question, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="question_images/")

    def __str__(self) -> str:
        return f"Image for {self.question.name} ({self.id})"
