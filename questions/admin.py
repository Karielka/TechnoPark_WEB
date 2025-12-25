from django.contrib import admin
from questions.models import Question, Answer, Tag, AnswerMark, QuestionMark

admin.site.register(QuestionMark)
admin.site.register(Question)
admin.site.register(AnswerMark)
admin.site.register(Answer)
admin.site.register(Tag)
