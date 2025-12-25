# users/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={
            "class": "form-control", 
            "placeholder": "Имя пользователя",
    }))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "class": "form-control", 
            "placeholder": "Пароль",
    }))


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "password1", "password2")
        labels = {"username": "Логин"}

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            UserProfile.objects.get_or_create(user=user)
        return user


class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Почта")
    display_name = forms.CharField(required=False, label="Имя")
    avatar = forms.ImageField(required=False, label="Фото")

    class Meta:
        model = UserProfile
        fields = ("display_name", "avatar")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["email"].initial = user.email
        self.fields["display_name"].initial = self.instance.display_name

    def save(self, commit=True):
        self.user.email = self.cleaned_data["email"].strip()
        if commit:
            self.user.save()
        self.instance.display_name = self.cleaned_data.get("display_name", "").strip()
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            self.instance.avatar = avatar
        if commit:
            self.instance.save()
        return self.instance