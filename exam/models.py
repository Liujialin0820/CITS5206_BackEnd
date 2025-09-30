# exams/models.py
from django.db import models
from django.utils import timezone
from django.db.models import F
import uuid

from testpaper.models import TestPaper
from questions.models import Question, Choice

class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    student_no = models.CharField(max_length=64, unique=True, db_index=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student_no} - {self.name}'

class Attempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    paper = models.ForeignKey(TestPaper, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name='attempts')

    started_at = models.DateTimeField()
    submitted_at = models.DateTimeField(blank=True, null=True)

    duration_seconds = models.PositiveIntegerField(default=0)
    score = models.FloatField(default=0)
    total_marks = models.FloatField(default=0)

    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    meta = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f'Attempt {self.id} of {self.student} on {self.paper}'

class AttemptAnswer(models.Model):
    attempt = models.ForeignKey(Attempt, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    selected_choice_ids = models.JSONField(default=list, blank=True)
    text_answer = models.TextField(blank=True, default='')
    is_correct = models.BooleanField(default=False)
    marks_awarded = models.FloatField(default=0)
    time_spent = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('attempt', 'question')

class QuestionStat(models.Model):
    """题目维度的累计：多少人答、答对/答错次数"""
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='stat')
    correct_count = models.PositiveIntegerField(default=0)
    wrong_count = models.PositiveIntegerField(default=0)
    attempts_count = models.PositiveIntegerField(default=0)

    def bump(self, correct: bool):
        self.attempts_count = F('attempts_count') + 1
        if correct:
            self.correct_count = F('correct_count') + 1
        else:
            self.wrong_count = F('wrong_count') + 1
        self.save(update_fields=['attempts_count', 'correct_count', 'wrong_count'])
        self.refresh_from_db()

class ChoiceStat(models.Model):
    """
    选项维度的累计：
    - selected_count：该选项被点了多少次（无论对错）
    - wrong_selected_count：该选项为“错误选项”时，被点了多少次（大家误选它的次数）
    """
    choice = models.OneToOneField(Choice, on_delete=models.CASCADE, related_name='stat')
    selected_count = models.PositiveIntegerField(default=0)
    wrong_selected_count = models.PositiveIntegerField(default=0)

    def bump(self, is_wrong_choice: bool):
        self.selected_count = F('selected_count') + 1
        if is_wrong_choice:
            self.wrong_selected_count = F('wrong_selected_count') + 1
        self.save(update_fields=['selected_count', 'wrong_selected_count'])
        self.refresh_from_db()
