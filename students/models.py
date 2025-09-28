# students/models.py
from django.db import models


class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)  # 学号
    name = models.CharField(max_length=100)  # 姓名
    email = models.EmailField(unique=True)  # 邮箱
    registration_date = models.DateTimeField()  # 注册日期

    class Meta:
        ordering = ["-registration_date"]

    def __str__(self):
        return f"{self.student_id} - {self.name}"
