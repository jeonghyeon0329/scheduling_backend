from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = "(core)사용자"
        verbose_name_plural = "(core)사용자 목록"

    def __str__(self):
        return self.username or self.email
