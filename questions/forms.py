from django import forms
from .models import Question, Answer


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        max_length=1000,
        label="Список тэгов",
        widget=forms.TextInput(attrs={"id": "tags", "name": "tags"}),
    )
    cover = forms.ImageField(
        required=False,
        label="Обложка",
        widget=forms.ClearableFileInput(attrs={"id": "cover", "name": "cover"}),
    )

    class Meta:
        model = Question
        fields = ["topic", "text", "cover", "tags"]
        widgets = {
            "topic": forms.TextInput(attrs={"id": "title", "name": "title"}),
            "text": forms.Textarea(attrs={"id": "question-text", "name": "text", "rows": 6}),
        }

    def clean_tags(self):
        raw = self.cleaned_data.get("tags", "")
        raw = raw.strip()
        if not raw:
            return []

        parts = raw.replace(",", ";", ".").split()
        parts = [p.strip() for p in parts if p.strip()]

        result = []
        for p in parts:
            if len(p) > 400:
                raise forms.ValidationError("Длина тэга не должна превышать 400 символов.")
            if p not in result:
                result.append(p)

        if len(result) > 20:
            raise forms.ValidationError("Слишком много тэгов (максимум 20).")

        return result


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={
                "class": "user-answer",
                "rows": 4,
                "placeholder": "Введите Ваш ответ",
            }),
        }

    def clean_text(self):
        text = (self.cleaned_data.get("text") or "").strip()
        if not text:
            raise forms.ValidationError("Текст ответа не может быть пустым.")
        return text
