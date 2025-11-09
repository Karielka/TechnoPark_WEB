from .models import Question, Tag
from django.db.models import Q

class QuestionManager():
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
        questions = Question.objects.all().order_by('-rating', '-answer_count', '-created_at')
        return self._get_question_by_page(questions, page_number)


    def get_new_question(self, page_number = 1):
        questions = Question.objects.all().order_by('-created_at')
        return self._get_question_by_page(questions, page_number)


    def get_tag_question(self, tag, page_number = 1):
        if not tag:
            questions = Question.objects.all()
        elif isinstance(tag, Tag):
            questions = Question.objects.filter(tags=tag)
        elif isinstance(tag, int):
            questions = Question.objects.filter(Q(tags__id=tag))
        else:
            questions = Question.objects.filter(Q(tags__title=tag))
        questions = questions.order_by('-created_at').distinct()

        return self._get_question_by_page(questions, page_number)