from django.core.management.base import BaseCommand
import random
from faker import Faker
from collections import defaultdict

from django.contrib.auth.models import User
from users.models import UserProfile
from questions.models import Question, Answer, Tag, QuestionMark, AnswerMark

def distribute(total, n):
    base, rem = divmod(total, n)
    sizes = [base] * n
    for i in random.sample(range(n), rem):
        sizes[i] += 1
    return sizes


class Command(BaseCommand):
    help = "Создаём тестовые данные для базы данных"

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **kwargs):
        ratio = kwargs.get("ratio")
        fake = Faker('ru_RU')
        fake.unique.clear()

        num_users = ratio
        num_tags = ratio
        num_questions = ratio * 10
        num_answers = ratio * 100
        num_marks = ratio * 200

        user_ids = []
        for i in range(num_users):
            temp_user, _ = User.objects.update_or_create(
                username=f'user_{i}',
                defaults={"email": fake.email()},
            )
            user_ids.append(temp_user.id)
            UserProfile.objects.update_or_create(
                user=temp_user,
                defaults={"display_name": fake.user_name(), "is_admin": False},
            )

        tag_ids, seen_titles = [], set()
        attempts, max_attempts = 0, num_tags * 3
        while len(tag_ids) < num_tags and attempts < max_attempts:
            attempts += 1
            title = fake.pystr(min_chars=6, max_chars=24)[:350]
            if title in seen_titles:
                continue
            tag, created = Tag.objects.get_or_create(title=title)
            if created:
                tag_ids.append(tag.id)
                seen_titles.add(title)


        question_ids = []
        for _ in range(num_questions):
            q = Question.objects.create(
                user_id=random.choice(user_ids),
                topic=fake.sentence(nb_words=8)[:500],
                text=fake.paragraph(nb_sentences=4),
            )
            if tag_ids:
                for t in random.sample(tag_ids, k=min(random.randint(1, 5), len(tag_ids))):
                    q.tags.add(t)
            question_ids.append(q.id)


        answer_ids = []
        answer_author = {}
        user_to_questions_answered = defaultdict(set)
        for _ in range(num_answers):
            qid = random.choice(question_ids)
            u_id = random.choice(user_ids)
            a = Answer.objects.create(
                question_id=qid,
                user_id=u_id,
                text=fake.paragraph(nb_sentences=3),
                is_correct=random.choice([True, False]),
            )
            answer_ids.append(a.id)
            answer_author[a.id] = u_id
            user_to_questions_answered[u_id].add(qid)


        like_value = [-1, 1]
        num_q_marks = num_marks // 2
        num_a_marks = num_marks - num_q_marks


        per_user_q = distribute(num_q_marks, len(user_ids))
        for u_id, quota in zip(user_ids, per_user_q):
            pool = list(user_to_questions_answered.get(u_id, []))
            if not pool:
                continue
            take = min(quota, len(pool))
            for qid in random.sample(pool, take):
                QuestionMark.objects.get_or_create(
                    user_id=u_id, 
                    question_id=qid,
                    defaults={"mark": random.choice(like_value)},
                )

        per_user_a = distribute(num_a_marks, len(user_ids))
        for u_id, quota in zip(user_ids, per_user_a):
            pool = [aid for aid in answer_ids if answer_author[aid] != u_id]
            if not pool:
                continue

            take = min(quota, len(pool))
            for aid in random.sample(pool, take):
                AnswerMark.objects.get_or_create(
                    user_id=u_id, 
                    answer_id=aid,
                    defaults={"mark": random.choice(like_value)},
                )

        self.stdout.write(self.style.SUCCESS("Данные успешно созданы"))
