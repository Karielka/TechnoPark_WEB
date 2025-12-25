from django.conf import settings
from django.db import models
from .managers import QuestionManager


class Question(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="user_questions",
        verbose_name="Автор",
    )
    topic = models.CharField(
        null=False,
        blank=False,
        max_length=500,
        verbose_name="Тема вопроса",
    )
    text = models.TextField(
        null=False,
        blank=False,
        verbose_name="Текст вопроса",
    )
    tags = models.ManyToManyField(
        "Tag",
        blank=True,
        verbose_name="Тэги",
    )
    answer_count = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        verbose_name="Количество ответов",
    )
    rating = models.IntegerField(
        default=0,
        blank=False,
        null=True,
        db_index=True,
        verbose_name="Рейтинг"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        db_index=True,
        verbose_name="Время создания",
    )

    objects = QuestionManager()


    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        

    def __str__(self):
        return f"Вопрос {self.id} от пользователя {self.user_id}"
    

    def add_answer(self):
        self.answer_count += 1
        self.save(update_fields=['answer_count'])


    def add_mark(self, mark):
        self.rating = (self.rating or 0) + mark
        self.save(update_fields=['rating'])


class Answer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="user_answers",
        verbose_name="Автор",
    )
    question = models.ForeignKey(
        "Question",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="question_answers",
        verbose_name="Вопрос",
    )
    text = models.TextField(
        blank=False,
        verbose_name="Текст ответа",
    )
    is_correct = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        verbose_name="Ответ правильный",
    )
    rating = models.IntegerField(
        default=0,
        blank=False,
        null=True,
        db_index=True,
        verbose_name="Рейтинг"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        db_index=True,
        verbose_name="Время создания",
    )


    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        indexes = [models.Index(fields=['question']),]


    def __str__(self):
        return f"Ответ {self.id} от пользователя {self.user_id} на вопрос {self.question_id}"
    

    def add_mark(self, mark):
        self.rating = (self.rating or 0) + mark
        self.save(update_fields=['rating'])


class Tag(models.Model):
    title = models.CharField(
        max_length=400,
        blank=False,
        null=False,
        unique=True,
        db_index=True,
    )


    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"
        

    def __str__(self):
        return f"Тэг {self.id}: {self.title} "
    

class QuestionMark(models.Model):

    class Values(models.IntegerChoices):
        Like = 1
        Dislike = -1

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="user_question_marks",
        verbose_name="Автор",
    )
    question = models.ForeignKey(
        "Question",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="question_marks",
        verbose_name="Вопрос",
    )
    mark = models.SmallIntegerField(
        blank=False,
        null=False,
        choices=Values.choices,
        verbose_name="Оценка",
    )


    class Meta:
        verbose_name = "Оценка вопроса"
        verbose_name_plural = "Оценки вопросов"
        unique_together = ["user", "question"]
        

    def __str__(self):
        return f"Оценка с id = {self.id}: {self.mark} для вопроса {self.question_id}"


class AnswerMark(models.Model):

    class Values(models.IntegerChoices):
        Like = 1
        Dislike = -1

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="user_answer_marks",
        verbose_name="Автор",
    )
    answer = models.ForeignKey(
        "Answer",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="answer_marks",
        verbose_name="Ответ",
    )
    mark = models.SmallIntegerField(
        blank=False,
        null=False,
        choices=Values.choices,
        verbose_name="Оценка",
    )


    class Meta:
        verbose_name = "Оценка ответа"
        verbose_name_plural = "Оценки ответов"
        unique_together = ["user", "answer"]


    def __str__(self):
        return f"Оценка с id = {self.id}: {self.mark} для ответа {self.answer_id}"