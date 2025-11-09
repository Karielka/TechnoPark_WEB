from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="profile",
        verbose_name="Пользователь Django",
    )
    display_name = models.CharField(
        max_length=150, 
        blank=True,
        verbose_name="Отображаемое имя",
    )
    avatar = models.ImageField(
        upload_to="avatars/%Y/%m/", 
        blank=True, 
        null=True,
        verbose_name="Аватар",
    )
    is_admin = models.BooleanField(
        default=False,
        verbose_name="Админ",
    )


    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"


    def __str__(self):
        return f"Профиль {self.user.username}, {self.user.email}"


    @property
    def avatar_url(self) -> str | None:
        from django.templatetags.static import static
        if self.avatar:
            try:
                return self.avatar.url
            except Exception:
                return None
        return static("img/avatar.png")
