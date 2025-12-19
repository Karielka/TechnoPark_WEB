from django.core.management.base import BaseCommand
import random
from faker import Faker
from collections import defaultdict

from django.contrib.auth.models import User
from django.db.models import Max
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
        parser.add_argument('ratio', nargs='?', type=int, default=100)

    def handle(self, *args, **kwargs):
        ratio = kwargs.get("ratio") or 100
        fake = Faker('ru_RU')
        fake.unique.clear()

        num_users = ratio
        num_tags = ratio
        num_questions = ratio * 10
        num_answers = ratio * 100
        num_marks = ratio * 200

        batch_size = 2000

        usernames = [f'user_{i}' for i in range(num_users)]

        users_to_create = []
        for i in range(num_users):
            users_to_create.append(
                User(username=f'user_{i}', email=fake.email())
            )
        User.objects.bulk_create(users_to_create, batch_size=batch_size, ignore_conflicts=True)

        user_ids = list(
            User.objects.filter(username__in=usernames).values_list('id', flat=True)
        )

        profiles_to_create = []
        for u_id in user_ids:
            profiles_to_create.append(
                UserProfile(user_id=u_id, display_name=fake.user_name(), is_admin=False)
            )
        UserProfile.objects.bulk_create(profiles_to_create, batch_size=batch_size, ignore_conflicts=True)

        tag_ids, seen_titles = [], set()
        attempts, max_attempts = 0, num_tags * 3
        while len(seen_titles) < num_tags and attempts < max_attempts:
            attempts += 1
            title = fake.pystr(min_chars=6, max_chars=24)[:350]
            seen_titles.add(title)

        tags_to_create = []
        for title in seen_titles:
            tags_to_create.append(Tag(title=title))
        Tag.objects.bulk_create(tags_to_create, batch_size=batch_size, ignore_conflicts=True)

        tag_ids = list(Tag.objects.filter(title__in=seen_titles).values_list('id', flat=True))

        q_max_id = Question.objects.aggregate(m=Max("id"))["m"] or 0

        questions_to_create = []
        for _ in range(num_questions):
            questions_to_create.append(
                Question(
                    user_id=random.choice(user_ids),
                    topic=fake.sentence(nb_words=8)[:500],
                    text=fake.paragraph(nb_sentences=4),
                )
            )
        Question.objects.bulk_create(questions_to_create, batch_size=batch_size)

        question_ids = list(
            Question.objects.filter(id__gt=q_max_id).values_list("id", flat=True)
        )

        if tag_ids:
            through_model = Question.tags.through
            links_to_create = []
            for qid in question_ids:
                for tid in random.sample(tag_ids, k=min(random.randint(1, 5), len(tag_ids))):
                    links_to_create.append(
                        through_model(question_id=qid, tag_id=tid)
                    )
            through_model.objects.bulk_create(links_to_create, batch_size=batch_size, ignore_conflicts=True)


        a_max_id = Answer.objects.aggregate(m=Max("id"))["m"] or 0

        answers_to_create = []
        user_to_questions_answered = defaultdict(set)

        for _ in range(num_answers):
            qid = random.choice(question_ids)
            u_id = random.choice(user_ids)

            answers_to_create.append(
                Answer(
                    question_id=qid,
                    user_id=u_id,
                    text=fake.paragraph(nb_sentences=3),
                    is_correct=random.choice([True, False]),
                )
            )
            user_to_questions_answered[u_id].add(qid)

        Answer.objects.bulk_create(answers_to_create, batch_size=batch_size)

        new_answers = list(
            Answer.objects.filter(id__gt=a_max_id).values_list("id", "user_id")
        )
        answer_ids = [aid for aid, _ in new_answers]
        answer_author = {aid: uid for aid, uid in new_answers}

        like_value = [-1, 1]
        num_q_marks = num_marks // 2
        num_a_marks = num_marks - num_q_marks

        qmarks_to_create = []
        per_user_q = distribute(num_q_marks, len(user_ids))
        for u_id, quota in zip(user_ids, per_user_q):
            pool = list(user_to_questions_answered.get(u_id, []))
            if not pool:
                continue

            take = min(quota, len(pool))
            for qid in random.sample(pool, take):
                qmarks_to_create.append(
                    QuestionMark(
                        user_id=u_id,
                        question_id=qid,
                        mark=random.choice(like_value),
                    )
                )

        QuestionMark.objects.bulk_create(qmarks_to_create, batch_size=batch_size, ignore_conflicts=True)

        amarks_to_create = []
        per_user_a = distribute(num_a_marks, len(user_ids))
        for u_id, quota in zip(user_ids, per_user_a):
            pool = [aid for aid in answer_ids if answer_author[aid] != u_id]
            if not pool:
                continue

            take = min(quota, len(pool))
            for aid in random.sample(pool, take):
                amarks_to_create.append(
                    AnswerMark(
                        user_id=u_id,
                        answer_id=aid,
                        mark=random.choice(like_value),
                    )
                )

        AnswerMark.objects.bulk_create(amarks_to_create, batch_size=batch_size, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS("Данные успешно созданы"))
