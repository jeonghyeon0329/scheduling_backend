from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = "(임시)사용자"
        verbose_name_plural = "(임시)사용자 목록"

    def __str__(self):
        return self.username or self.email


class ExternalUser(models.Model):
    external_user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="HR 사용자 ID"
    )
    username = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="사용자명"
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name="이메일"
    )
    status = models.CharField(
        max_length=20,
        default="active",
        verbose_name="상태"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "external_user"
        verbose_name = "외부 사용자"
        verbose_name_plural = "외부 사용자 목록"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.email})"