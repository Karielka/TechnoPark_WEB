from django.db.models import Q
from django.db import models
from django.apps import apps


class QuestionManager(models.Manager):
    QUESTION_COUNT_PAGE = 10

    def _get_question_by_page(self, questions, page_number = 1):
        try:
            page_number = int(page_number)
        except (TypeError, ValueError):
            page_number = 1
        if page_number < 1:
            page_number = 1

        question_count = questions.count()
        all_page_count = (question_count // self.QUESTION_COUNT_PAGE) 
        if (question_count % self.QUESTION_COUNT_PAGE) > 0:
            all_page_count += 1
        if all_page_count == 0:
            all_page_count = 1

        start = (page_number - 1) * self.QUESTION_COUNT_PAGE
        end = start + self.QUESTION_COUNT_PAGE

        if start > question_count:
            start = 0
            end = self.QUESTION_COUNT_PAGE
        if end > question_count:
            end = question_count

        return [questions[start:end], all_page_count]


    def get_hot_question(self, page_number = 1):
        questions = self.get_queryset().order_by('-rating', '-answer_count', '-created_at')
        return self._get_question_by_page(questions, page_number)


    def get_new_question(self, page_number = 1):
        questions = self.get_queryset().order_by('-created_at')
        return self._get_question_by_page(questions, page_number)


    def get_tag_question(self, tag, page_number = 1):
        Tag = apps.get_model('questions', 'Tag')

        if not tag:
            questions = self.get_queryset()
        elif isinstance(tag, Tag):
            questions = self.get_queryset().filter(tags=tag)
        elif isinstance(tag, int):
            questions = self.get_queryset().filter(Q(tags__id=tag))
        else:
            questions = self.get_queryset().filter(Q(tags__title=tag))
        questions = questions.order_by('-created_at').distinct()

        return self._get_question_by_page(questions, page_number)