# exams/serializers.py
from rest_framework import serializers
from django.utils import timezone
from django.db import transaction

from .models import Student, Attempt, AttemptAnswer, QuestionStat, ChoiceStat
from testpaper.models import TestPaper
from questions.models import Question, Choice

class StudentInlineSerializer(serializers.Serializer):
    name = serializers.CharField()
    student_no = serializers.CharField()
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)

class StartExamSerializer(serializers.Serializer):
    paper_id = serializers.IntegerField()
    student = StudentInlineSerializer()
    started_at = serializers.DateTimeField(required=False)

    def create(self, validated_data):
        s = validated_data['student']
        student, _ = Student.objects.get_or_create(
            student_no=s['student_no'],
            defaults={'name': s['name'], 'email': s.get('email') or ''}
        )
        dirty = False
        if student.name != s['name']:
            student.name = s['name']; dirty = True
        if s.get('email') and student.email != s.get('email'):
            student.email = s['email']; dirty = True
        if dirty: student.save()

        paper = TestPaper.objects.get(id=validated_data['paper_id'])
        started_at = validated_data.get('started_at') or timezone.now()

        attempt = Attempt.objects.create(
            paper=paper,
            student=student,
            started_at=started_at,
        )
        return attempt

class SubmitAnswerItemSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_choice_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    text_answer = serializers.CharField(required=False, allow_blank=True)
    time_spent = serializers.IntegerField(required=False, default=0)

class SubmitExamSerializer(serializers.Serializer):
    attempt_token = serializers.UUIDField()
    submitted_at = serializers.DateTimeField(required=False)
    duration_seconds = serializers.IntegerField(required=False)
    answers = SubmitAnswerItemSerializer(many=True)

    def _score_one(self, question: Question, selected_choice_ids, text_answer):
        qtype = question.type
        correct_ids = set(question.choices.filter(is_correct=True).values_list('id', flat=True))

        if qtype == 'Single Choice':
            sel = list(selected_choice_ids or [])
            ok = (len(sel) == 1 and sel[0] in correct_ids)
            return ok, (float(question.marks) if ok else 0.0)

        if qtype == 'Multiple Choice':
            sel = set(selected_choice_ids or [])
            ok = (sel == correct_ids)
            return ok, (float(question.marks) if ok else 0.0)

        return False, 0.0

    def create(self, validated_data):
        from django.db.models import Sum, F

        with transaction.atomic():
            attempt = Attempt.objects.select_for_update().get(
                attempt_token=validated_data['attempt_token']
            )
            if attempt.submitted_at:
                raise serializers.ValidationError('This attempt was already submitted.')

            submitted_at = validated_data.get('submitted_at') or timezone.now()
            answers_payload = validated_data['answers']

            # 预取题与选项 -> {qid: Question}, {cid: is_correct}
            q_ids = [a['question_id'] for a in answers_payload]
            questions = list(Question.objects.filter(id__in=q_ids).prefetch_related('choices'))
            qmap = {q.id: q for q in questions}
            choice_is_correct = {}
            for q in questions:
                for c in q.choices.all():
                    choice_is_correct[c.id] = c.is_correct

            total_marks = 0.0
            score = 0.0
            aa_bulk = []

            # 先把所有被点击的选项聚合计数（减少 DB 调用）
            per_choice_delta = {}  # cid -> {'sel': n, 'wrong': n}
            def bump_choice(cid, is_wrong):
                d = per_choice_delta.setdefault(cid, {'sel':0, 'wrong':0})
                d['sel'] += 1
                if is_wrong:
                    d['wrong'] += 1

            for item in answers_payload:
                q = qmap[item['question_id']]
                total_marks += float(q.marks)

                sel = item.get('selected_choice_ids') or []
                txt = item.get('text_answer', '')
                tsec = int(item.get('time_spent') or 0)

                ok, got = self._score_one(q, sel, txt)
                score += got

                # 记录 AttemptAnswer
                aa_bulk.append(AttemptAnswer(
                    attempt=attempt,
                    question=q,
                    selected_choice_ids=list(sel),
                    text_answer=txt,
                    is_correct=ok,
                    marks_awarded=got,
                    time_spent=tsec
                ))

                # 选项维度聚合（特别是错误选项）
                for cid in sel:
                    is_wrong_choice = not choice_is_correct.get(cid, False)
                    bump_choice(cid, is_wrong_choice)

            AttemptAnswer.objects.bulk_create(aa_bulk)

            # 更新 Attempt 汇总
            attempt.total_marks = total_marks
            attempt.score = score
            attempt.submitted_at = submitted_at
            attempt.duration_seconds = int((attempt.submitted_at - attempt.started_at).total_seconds())
            attempt.save(update_fields=['total_marks', 'score', 'submitted_at', 'duration_seconds'])

            # 题目维度增量
            for aa in aa_bulk:
                stat, _ = QuestionStat.objects.get_or_create(question=aa.question)
                stat.bump(aa.is_correct)

            # 选项维度增量（一次性应用所有变化）
            for cid, delta in per_choice_delta.items():
                stat, _ = ChoiceStat.objects.get_or_create(choice_id=cid)
                # 用 F 表达式叠加
                ChoiceStat.objects.filter(pk=stat.pk).update(
                    selected_count=F('selected_count') + delta['sel'],
                    wrong_selected_count=F('wrong_selected_count') + delta['wrong']
                )

        return attempt
