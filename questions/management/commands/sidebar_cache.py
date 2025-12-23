from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Q, Sum, F
from django.db.models.functions import Coalesce
from django.contrib.auth import get_user_model

from questions.models import Question, Tag
from questions.caches import LatestQuestionsCache, PopularTagsCache, BestMembersCache


class Command(BaseCommand):
    help = "Обновление кэша"

    def handle(self, *args, **options):
        now = timezone.now()

        # 1) 10 последних вопросов
        latest_questions_qs = (
            Question.objects
            .select_related("user")
            .order_by("-created_at")
            .only("id", "topic", "created_at", "rating", "answer_count", "user_id", "user__username")[:10]
        )

        latest_questions_items = [
            {
                "id": q.id,
                "topic": q.topic,
                "created_at": q.created_at,
                "rating": q.rating or 0,
                "answer_count": q.answer_count,
                "user_id": q.user_id,
                "username": getattr(q.user, "username", str(q.user_id)),
            }
            for q in latest_questions_qs
        ]
        LatestQuestionsCache.set_items(latest_questions_items)

        # 2) Популярные теги за 3 месяца
        three_months_ago = now - timedelta(days=90)
        popular_tags_qs = (
            Tag.objects
            .annotate(
                questions_count=Count(
                    "question",
                    filter=Q(question__created_at__gte=three_months_ago),
                    distinct=True,
                )
            )
            .filter(questions_count__gt=0)
            .order_by("-questions_count", "title")
            .only("id", "title")[:10]
        )

        popular_tags_items = [
            {"id": t.id, "title": t.title, "questions_count": t.questions_count}
            for t in popular_tags_qs
        ]
        PopularTagsCache.set_items(popular_tags_items)

        # 3) Лучшие пользователи за неделю:
        #    по сумме рейтингов вопросов и ответов, созданных за последнюю неделю
        week_ago = now - timedelta(days=7)
        User = get_user_model()

        best_members_qs = (
            User.objects
            .annotate(
                q_score=Coalesce(
                    Sum("user_questions__rating", filter=Q(user_questions__created_at__gte=week_ago)),
                    0
                ),
                a_score=Coalesce(
                    Sum("user_answers__rating", filter=Q(user_answers__created_at__gte=week_ago)),
                    0
                ),
            )
            .annotate(score=F("q_score") + F("a_score"))
            .filter(score__gt=0)
            .order_by("-score", "username")
            .only("id", "username")[:10]
        )

        best_members_items = [
            {"id": u.id, "username": getattr(u, "username", str(u.id)), "score": u.score}
            for u in best_members_qs
        ]
        BestMembersCache.set_items(best_members_items)

        self.stdout.write(self.style.SUCCESS(
            f"Cache warmed: latest_questions={len(latest_questions_items)}, "
            f"popular_tags={len(popular_tags_items)}, best_members={len(best_members_items)}"
        ))
