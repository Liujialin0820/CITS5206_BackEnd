# exams/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg, Sum, Count, Max, Q, F, Value
from django.db.models.functions import Coalesce

from .serializers import StartExamSerializer, SubmitExamSerializer
from .models import Attempt, AttemptAnswer, ChoiceStat
from questions.models import Choice
from testpaper.models import TestPaper
from students.models import Student


class GlobalStatsAPI(APIView):
    """
    GET /api/admin/global-stats/
    统计：学生数、试卷数、题目数、尝试数 + 各 Level 数据
    """

    def get(self, request):
        # === 顶部统计 ===
        student_count = Student.objects.count()
        paper_count = TestPaper.objects.count()
        question_count = Question.objects.count()
        attempt_count = Attempt.objects.filter(submitted_at__isnull=False).count()

        # === 分 Level 统计 ===
        levels = ["Level 1", "Level 2", "Level 3", "Level 4"]
        stats = {}

        for level in levels:
            # 题目数
            q_count = Question.objects.filter(level=level).count()

            # 所有已提交的 attempts
            attempts = Attempt.objects.filter(
                paper__level=level, submitted_at__isnull=False
            )

            # 有尝试的学生数（distinct）
            student_in_level = attempts.values("student").distinct().count()

            # 通过人数（score >= pass_percentage%）
            passed_students = attempts.filter(
                score__gte=F("total_marks") * F("paper__pass_percentage") / 100.0
            ).values("student").distinct().count()

            # 正确率
            answers = AttemptAnswer.objects.filter(question__level=level)
            total_answers = answers.count() or 1
            correct_answers = answers.filter(is_correct=True).count()
            accuracy = round(correct_answers / total_answers * 100, 2)

            stats[level] = {
                "students": student_in_level,
                "passed_students": passed_students,
                "questions": q_count,
                "accuracy": accuracy,
            }

        return Response(
            {
                "student_count": student_count,
                "paper_count": paper_count,
                "question_count": question_count,
                "attempt_count": attempt_count,
                "levels": stats,
            },
            status=status.HTTP_200_OK,
        )

class PaperResultAPI(APIView):
    """
    GET /api/admin/papers/<paper_id>/result/
    返回这个试卷的学生成绩统计
    """
    def get(self, request, paper_id):
        try:
            paper = TestPaper.objects.get(id=paper_id)
        except TestPaper.DoesNotExist:
            return Response({"detail": "TestPaper not found"}, status=status.HTTP_404_NOT_FOUND)

        attempts = Attempt.objects.filter(paper_id=paper_id).select_related("student")

        rows = []
        for a in attempts:
            rows.append({
                "student_id": str(a.student.id),
                "student_no": a.student.student_no,
                "student_name": a.student.name,
                "score": a.score,
                "total_marks": a.total_marks,
                "submitted_at": a.submitted_at,
            })

        return Response({
            "paper_id": paper_id,
            "paper_title": paper.title,
            "attempts_count": attempts.count(),
            "attempts": rows
        })

def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

class StartExamAPI(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        ser = StartExamSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        attempt = ser.save()
        attempt.user_agent = request.META.get('HTTP_USER_AGENT', '')
        attempt.ip_address = _client_ip(request)
        attempt.save(update_fields=['user_agent', 'ip_address'])

        return Response({
            'attempt_id': str(attempt.id),
            'attempt_token': str(attempt.attempt_token),
            'paper_id': attempt.paper_id,
            'started_at': attempt.started_at.isoformat(),
        }, status=status.HTTP_201_CREATED)

class SubmitExamAPI(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        ser = SubmitExamSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        attempt = ser.save()

        details = AttemptAnswer.objects.filter(attempt=attempt).values(
            'question_id', 'is_correct', 'marks_awarded', 'selected_choice_ids', 'text_answer'
        )
        return Response({
            'attempt_id': str(attempt.id),
            'paper_id': attempt.paper_id,
            'student_no': attempt.student.student_no,
            'name': attempt.student.name,
            'score': attempt.score,
            'total_marks': attempt.total_marks,
            'duration_seconds': attempt.duration_seconds,
            'submitted_at': attempt.submitted_at.isoformat(),
            'details': list(details),
        }, status=status.HTTP_200_OK)

class PaperStatsAPI(APIView):
    """
    GET /api/admin/papers/<paper_id>/stats
    可选参数：?wrong_choices=1  -> 返回每题“错误选项分布”
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request, paper_id: int):
        # 总体
        attempts = Attempt.objects.filter(paper_id=paper_id, submitted_at__isnull=False)
        summary = attempts.aggregate(
            total_attempts=Count('id'),
            avg_score=Avg('score'),
            max_score=Max('score'),
            avg_duration=Avg('duration_seconds'),
            sum_score=Sum('score'),
        )

        # 每题聚合
        per_q = (AttemptAnswer.objects
                 .filter(attempt__paper_id=paper_id)
                 .values('question_id')
                 .annotate(
                     attempts=Count('id'),
                     correct=Count('id', filter=Q(is_correct=True)),
                     wrong=Count('id', filter=Q(is_correct=False)),
                     avg_marks=Avg('marks_awarded'),
                 )
                 .order_by('question_id'))

        data = {
            'paper_id': int(paper_id),
            'summary': summary,
            'by_question': list(per_q),
        }

        # 可选返回：每题错误选项分布
        want_wrong = request.query_params.get('wrong_choices') in ('1', 'true', 'yes')
        if want_wrong:
            # 先拿到每题总作答次数（计算错误选项误选率时用）
            attempts_by_q = {row['question_id']: row['attempts'] for row in per_q}

            # 选出该试卷题目的所有“错误选项”，并联到 ChoiceStat
            wrong_choices = (Choice.objects
                             .filter(question_id__in=attempts_by_q.keys(), is_correct=False)
                             .select_related('question')
                             .annotate(
                                 selected=Coalesce(F('stat__selected_count'), Value(0)),
                                 wrong_selected=Coalesce(F('stat__wrong_selected_count'), Value(0)),
                             ))
            breakdown = {}
            for c in wrong_choices:
                qid = c.question_id
                total_attempts = attempts_by_q.get(qid, 0) or 1  # 防除零
                item = {
                    'choice_id': c.id,
                    'text': c.text,
                    'wrong_selected': int(c.wrong_selected),
                    'selected_total': int(c.selected),
                    'wrong_rate_per_attempt': float(c.wrong_selected) / float(total_attempts),
                }
                breakdown.setdefault(str(qid), []).append(item)

            # 每题内部按误选次数降序
            for qid, rows in breakdown.items():
                rows.sort(key=lambda x: x['wrong_selected'], reverse=True)

            data['wrong_choice_breakdown'] = breakdown

        return Response(data, status=status.HTTP_200_OK)

from questions.models import Question, Choice

class QuestionChoiceStatsAPI(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request, question_id: int):
        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            return Response({"detail": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        # 总作答次数
        attempts_cnt = AttemptAnswer.objects.filter(question_id=question_id).count() or 1

        # 选项统计
        choices = (Choice.objects
                    .filter(question_id=question_id)
                    .annotate(
                        selected=Coalesce(F('stat__selected_count'), Value(0)),
                        wrong_selected=Coalesce(F('stat__wrong_selected_count'), Value(0)),
                    )
                    .order_by('id'))

        rows = []
        for c in choices:
            rows.append({
                'choice_id': c.id,
                'text': c.text,
                'is_correct': c.is_correct,
                'selected_total': int(c.selected),
                'wrong_selected': int(c.wrong_selected),
                'wrong_rate_per_attempt': (float(c.wrong_selected) / float(attempts_cnt)),
            })

        rows.sort(key=lambda x: (x['is_correct'], -x['wrong_selected']))

        return Response({
            "id": question.id,
            "text": question.question_text,
            "type": question.type,
            "marks": question.marks,
            "category": question.category,
            "level": question.level,
            "attempts": attempts_cnt,
            "choices": rows
        }, status=status.HTTP_200_OK)