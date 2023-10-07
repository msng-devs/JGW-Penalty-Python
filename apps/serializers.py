# --------------------------------------------------------------------------
# Penalty Application의 Serializer를 정의한 모듈입니다.
#
# @author 이준혁(39기) bbbong9@gmail.com
# --------------------------------------------------------------------------
from __future__ import annotations

from django.core.validators import MinValueValidator

from rest_framework import serializers

from apps.common.models import Member
from apps.penalty.models import Penalty


class AbstractPenaltyRequestSerializer(serializers.ModelSerializer):
    target_member_id = serializers.CharField(
        source="target_member.id",
        max_length=28,
        min_length=28,
        error_messages={
            "blank": "UID가 비여있습니다!",
            "max_length": "UID는 28자리여야 합니다.",
            "min_length": "UID는 28자리여야 합니다.",
        },
    )

    class Meta:
        model = Penalty
        fields = [
            "target_member_id",
        ]

    def validate_target_member_id(self, value):
        """
        Check if the given member_id exists in the Member model.
        """
        if not Member.objects.filter(id=value).exists():
            raise serializers.ValidationError("해당 멤버는 존재하지 않습니다.")
        return value


class PenaltyAddRequestSerializer(AbstractPenaltyRequestSerializer):
    reason = serializers.CharField(
        max_length=255,
        error_messages={
            "blank": "사유는 공백으로 할 수 없습니다!",
            "max_length": "입력가능한 최대 글자수는 255자입니다.",
        },
    )
    type = serializers.BooleanField(error_messages={"null": "패널티의 종류가 누락되어있습니다!"})

    class Meta(AbstractPenaltyRequestSerializer.Meta):
        fields = AbstractPenaltyRequestSerializer.Meta.fields + ["id", "reason", "type"]

    def create(self, validated_data):
        target_member_id = validated_data.get("target_member").get("id")
        member = Member.objects.get(id=target_member_id)
        penalty = Penalty.objects.create(
            reason=validated_data.get("reason"),
            target_member=member,
            type=validated_data.get("type"),
        )
        return penalty


class PenaltyBulkDeleteRequestSerializer(serializers.ModelSerializer):
    penalty_ids = serializers.ListField(
        child=serializers.IntegerField(),
        error_messages={"required": "Penalty_ids가 비워져있습니다!"},
    )

    def validate_penalty_ids(self, value):
        if not isinstance(value, list) or not all(
            isinstance(item, int) for item in value
        ):
            raise serializers.ValidationError("Penalty_ids는 정수 리스트 형태여야 합니다.")
        return value

    def delete(self):
        Penalty.objects.filter(id__in=self.validated_data["penalty_ids"]).delete()

    class Meta:
        model = Penalty
        fields = ["penalty_ids"]


class PenaltyBulkUpdateRequestSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        # # ID별로 Penalty 객체 저장
        # penalty_mapping = {penalty.id: penalty for penalty in instance}

        # # ID로 전달된 데이터 저장
        # data_mapping = {item["id"]: item for item in validated_data}

        # # 업데이트할 Penalty 객체 리스트
        # updated_penalties = []

        # for penalty_id, data in data_mapping.items():
        #     penalty = penalty_mapping.get(penalty_id, None)
        #     if penalty:
        #         updated_penalties.append(self.child.update(penalty, data))

        # return updated_penalties
        updated_instances = []
        for obj_data in validated_data:
            obj = next((item for item in instance if item.id == obj_data["id"]), None)
            if obj:
                for attr, value in obj_data.items():
                    setattr(obj, attr, value)
                obj.save()
                updated_instances.append(obj)
        return updated_instances


class PenaltyUpdateRequestSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        validators=[MinValueValidator(1)],
        error_messages={"required": "id가 비워져 있습니다!", "min_value": "id의 형식이 잘못되었습니다!"},
        required=False,
    )
    reason = serializers.CharField(
        max_length=255,
        error_messages={
            "blank": "사유는 공백으로 할 수 없습니다!",
            "max_length": "입력가능한 최대 글자수는 255자입니다.",
        },
    )
    type = serializers.BooleanField(error_messages={"null": "패널티의 종류가 누락되어있습니다!"})

    class Meta(AbstractPenaltyRequestSerializer.Meta):
        model = Penalty
        fields = ["id", "reason", "type"]
        list_serializer_class = PenaltyBulkUpdateRequestSerializer


class PenaltyIdSerializer(serializers.ModelSerializer):
    penalty_id = serializers.IntegerField(source="id")

    class Meta:
        model = Penalty
        fields = ["penalty_id"]


class PenaltyResponseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    target_member_id = serializers.CharField(source="target_member.id")
    target_member_name = serializers.CharField(source="target_member.name")
    # modified_by = serializers.CharField(source="modifiedBy")
    type = serializers.BooleanField()
    reason = serializers.CharField()
    # created_by = serializers.CharField(source="createdBy")

    class Meta:
        model = Penalty
        fields = [
            "id",
            "target_member_id",
            "target_member_name",
            # "modified_by",
            "type",
            "reason",
            # "created_by",
            "created_date",
            "modified_date",
        ]
