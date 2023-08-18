from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Object의 생성 및 수정에 대한 기본적인 정보를 담은 추상 클래스
class BaseModel(models.Model):
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now)

    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="%(class)s_created_by"
    )
    modified_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="%(class)s_modified_by"
    )

    class Meta:
        abstract = True
