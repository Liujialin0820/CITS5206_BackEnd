# testpaper/models.py
from django.db import models
from questions.models import Question  # ✅ 直接关联已有的题目

class TestPaper(models.Model):
    STATUS_CHOICES = [
        ("Draft", "Draft"),
        ("Published", "Published"),
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

    title = models.CharField(max_length=255)
    level = models.CharField(max_length=50, choices=LEVELS, blank=True, null=True)
    category = models.CharField(max_length=100, choices=CATEGORIES, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Draft")
    questions = models.ManyToManyField(Question, related_name="test_papers")
    created_at = models.DateTimeField(auto_now_add=True)
    level_config = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def total_marks(self):
        return self.questions.aggregate(models.Sum("marks"))["marks__sum"] or 0
