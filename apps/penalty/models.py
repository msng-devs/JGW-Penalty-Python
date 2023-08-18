from django.db import models
from django.utils import timezone

from apps.base import BaseModel


class Penalty(BaseModel):
    # 해당 패널티의 ID(PK)
    id = models.AutoField(primary_key=True)

    # 해당 패널티가 부여된 Member(Object)
    target_member = models.ForeignKey(
        "member.Member", on_delete=models.CASCADE, null=False
    )

    # 해당 패널티의 유형(false면 경고, true면 주의)
    type = models.BooleanField(null=False)

    # 해당 패널티가 부여된 사유
    reason = models.CharField(max_length=255, null=False)

    # 패널티의 정보를 수정하는 함수
    def update(self, penalty, who):
        self.reason = penalty.reason
        self.type = penalty.type
        self.modified_by = who
        self.modified_date = timezone.now()

    class Meta:
        db_table = "PENALTY"
        ordering = ["-created_date"]
