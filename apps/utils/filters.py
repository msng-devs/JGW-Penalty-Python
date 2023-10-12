# --------------------------------------------------------------------------
# 쿼리파라미터를 통한 필터링을 구현하기 위한 모듈입니다.
#
# @author 이준혁(39기) bbbong9@gmail.com
# --------------------------------------------------------------------------
from django_filters import rest_framework as filters

from apps.penalty.models import Penalty


class BaseFilterSet(filters.FilterSet):
    """각 필터들의 부모 클래스입니다.

    이 클래스를 상속받아 각 모델에 맞는 필터를 구현합니다.
    """

    # Equal Query Options
    createdBy = filters.CharFilter(field_name="created_by")
    modifiedBy = filters.CharFilter(field_name="modified_by")

    # Range Query Options
    startCreatedDateTime = filters.DateTimeFilter(
        field_name="created_date_time", lookup_expr="gte"
    )
    endCreatedDateTime = filters.DateTimeFilter(
        field_name="created_date_time", lookup_expr="lte"
    )
    startModifiedDateTime = filters.DateTimeFilter(
        field_name="modified_date_time", lookup_expr="gte"
    )
    endModifiedDateTime = filters.DateTimeFilter(
        field_name="modified_date_time", lookup_expr="lte"
    )

    class Meta:
        abstract = True


class PenaltyFilter(BaseFilterSet):
    # Equal Query Options
    targetMember = filters.CharFilter(field_name="target_member_id")
    type = filters.BooleanFilter(field_name="type")

    # Like Query Options
    reason = filters.CharFilter(field_name="reason", lookup_expr="icontains")

    class Meta:
        model = Penalty
        fields = [
            "targetMember",
            "type",
            "reason",
            "createdBy",
            "modifiedBy",
            "startCreatedDateTime",
            "endCreatedDateTime",
            "startModifiedDateTime",
            "endModifiedDateTime",
        ]
