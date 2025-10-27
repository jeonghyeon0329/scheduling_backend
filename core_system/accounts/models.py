from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [] 


class UserStatus(models.TextChoices):
    PENDING   = "pending", "대기"
    ACTIVE    = "active", "활성"
    SUSPENDED = "suspended", "정지"


class ExternalUser(models.Model):
    external_user_id = models.UUIDField(
        unique=True,
        verbose_name="외부 사용자 ID",
        help_text="HR System에서 발급된 사용자 UUID"
    )
    email = models.EmailField(
        unique=True,
        db_index=True,
        verbose_name="이메일",
        help_text="사용자 이메일 주소 (검색 최적화 인덱스 포함)"
    )
    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.PENDING,
        verbose_name="상태",
        help_text="사용자 상태: pending, active, suspended 등"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="갱신일시",
        help_text="core_system에서 데이터가 마지막으로 갱신된 시간"
    )

    class Meta:
        verbose_name = "외부 사용자"
        verbose_name_plural = "외부 사용자 목록"
