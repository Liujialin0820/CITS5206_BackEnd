# students/models.py
from django.db import models
import uuid


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    student_no = models.CharField(max_length=64, unique=True, db_index=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)

    def __str__(self):
        return f'{self.student_no} - {self.name}'