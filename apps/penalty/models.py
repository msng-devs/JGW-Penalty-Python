# --------------------------------------------------------------------------
# Penalty Application의 Models를 정의한 모듈입니다.
#
# @author 이준혁(39기) bbbong9@gmail.com
# --------------------------------------------------------------------------
from django.db import models
from django.utils import timezone

from apps.common.models import Member


class Penalty(models.Model):
    # 해당 패널티의 ID(PK)
    id = models.AutoField(primary_key=True, db_column="PENALTY_PK")

    # 해당 패널티가 부여된 Member(Object)
    target_member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="penalty",
        db_column="MEMBER_MEMBER_PK",
    )

    # 해당 패널티의 유형(false면 경고, true면 주의)
    type = models.BooleanField(null=False, db_column="PENALTY_TYPE")

    # 해당 패널티가 부여된 사유
    reason = models.CharField(max_length=255, null=False, db_column="PENALTY_REASON")

    modified_date = models.DateTimeField(
        auto_now=True,
        verbose_name="Modified Date Time",
        db_column="PENALTY_MODIFIED_DTTM",
    )
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created Date Time",
        db_column="PENALTY_CREATED_DTTM",
    )
    created_by = models.CharField(
        max_length=30,
        verbose_name="Created By",
        default="system",
        db_column="PENALTY_CREATED_BY",
    )
    modified_by = models.CharField(
        max_length=30,
        verbose_name="Modified By",
        default="system",
        db_column="PENALTY_MODIFIED_BY",
    )

    # 패널티의 정보를 수정하는 함수
    def update(self, penalty, who):
        self.reason = penalty.reason
        self.type = penalty.type
        self.modified_by = who
        self.modified_date = timezone.now()

    class Meta:
        db_table = "PENALTY"
        verbose_name = "Penalty"
        verbose_name_plural = "Penalties"
