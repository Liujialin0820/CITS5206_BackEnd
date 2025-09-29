# testpaper/views.py
import random
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import TestPaper
from .serializers import TestPaperSerializer
from questions.models import Question
from questions.serializers import QuestionPreviewSerializer  # 你现有的读序列化器


class TestPaperViewSet(viewsets.ModelViewSet):
    queryset = TestPaper.objects.all()
    serializer_class = TestPaperSerializer

    @action(detail=True, methods=["get"])
    def generate(self, request, pk=None):
        """
        根据 level_config 临时生成题目（不保存到DB）：
        - mode == "count": 恰好抽取 exam_questions 道题；若不足则报错
        - mode == "marks": 恰好抽取总分 == total_marks；若凑不出来则报错
        返回：
        {
          ...paper,
          "generated_questions": [Question...],
          "summary": {
              "Level 1": {"mode": "count", "need": 4, "got": 4},
              "Level 2": {"mode": "marks", "need": 10, "got": 10},
              ...
          }
        }
        """
        paper = self.get_object()
        config = paper.level_config or {}

        all_selected = []
        summary = {}
        errors = []

        def pick_by_count(qs, count, level_name):
            pool = list(qs)
            if len(pool) < count:
                raise ValueError(
                    f"[{level_name}] Not enough questions: need {count}, only {len(pool)} available."
                )
            # 随机取恰好 count 道
            return random.sample(pool, count)

        def pick_by_marks(qs, target, level_name):
            """
            子集和DP：恰好等于 target
            dp[score] = 使用到的下标列表
            为了随机化，先洗牌
            """
            pool = list(qs)
            random.shuffle(pool)
            target = int(target)

            dp = {0: []}  # 分数 -> 使用的索引列表
            for idx, q in enumerate(pool):
                m = int(q.marks)
                # 遍历快照，避免一轮多次复用同一题
                for cur, used_idx in list(dp.items()):
                    new_sum = cur + m
                    if new_sum > target:
                        continue
                    if new_sum not in dp:  # 首次到达该分数
                        dp[new_sum] = used_idx + [idx]
                        if new_sum == target:
                            # 立即返回一组解
                            return [pool[i] for i in dp[new_sum]]

            # 没有恰好等于 target 的组合
            raise ValueError(
                f"[{level_name}] Cannot reach exact total marks = {target} with available questions."
            )

        # 遍历 level_config 各层级
        for level_name, rules in config.items():
            mode = rules.get("mode")
            level_qs = Question.objects.filter(level=level_name)

            if mode == "count":
                need = int(rules.get("exam_questions") or 0)
                got_list = []
                if need > 0:
                    try:
                        got_list = pick_by_count(level_qs, need, level_name)
                    except ValueError as e:
                        errors.append(str(e))
                summary[level_name] = {
                    "mode": "count",
                    "need": need,
                    "got": len(got_list),
                }
                all_selected.extend(got_list)

            elif mode == "marks":
                need = int(rules.get("total_marks") or 0)
                got_list = []
                if need > 0:
                    try:
                        got_list = pick_by_marks(level_qs, need, level_name)
                    except ValueError as e:
                        errors.append(str(e))
                # 统计 got 的总分
                got_marks = sum(q.marks for q in got_list)
                summary[level_name] = {"mode": "marks", "need": need, "got": got_marks}
                all_selected.extend(got_list)

            else:
                # 未配置或 mode 空
                summary[level_name] = {"mode": None, "need": 0, "got": 0}

        # 如果有任何层级失败，返回 400 和错误信息
        if errors:
            return Response(
                {"detail": "Generate failed", "errors": errors, "summary": summary},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 去重（跨层理论不会重复，但安全起见）
        seen = set()
        unique_selected = []
        for q in all_selected:
            if q.id not in seen:
                unique_selected.append(q)
                seen.add(q.id)

        # 序列化返回（不保存）
        paper_data = TestPaperSerializer(paper).data
        paper_data["generated_questions"] = QuestionPreviewSerializer(
            unique_selected, many=True
        ).data
        for key in ["level_config", "questions", "questions_detail", "status"]:
            paper_data.pop(key, None)
            
        return Response(paper_data, status=status.HTTP_200_OK)
