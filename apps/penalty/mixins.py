# --------------------------------------------------------------------------
# 서비스에 사용되는 Model Mixins를 정의한 모듈입니다.
#
# @author 이준혁(39기) bbbong9@gmail.com
# --------------------------------------------------------------------------
import logging

from rest_framework import mixins, status
from rest_framework.response import Response

from .models import Penalty

logger = logging.getLogger("django")


class CreateMultiPenaltyMixin(mixins.CreateModelMixin):
    """PenaltyList의 POST 메서드에 사용되는 Mixin.

    단일(dict), 다중(list) request 모두 수용하기 위해 is_many 라는 변수를 사용했습니다.
    """

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        penalties = serializer.save()

        if not isinstance(penalties, list):
            penalties = [penalties]

        for penalty in penalties:
            message = (
                f"User {penalty.target_member_id} added penalty with ID {penalty.id}"
            )
            logger.info(message)


class DestroyMultiPenaltyMixin(mixins.DestroyModelMixin):
    """PenaltyList의 DELETE 메서드에 사용되는 Mixin."""

    def destroy(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            Penalty.objects.filter(
                id__in=serializer.validated_data["penalty_ids"]
            ).delete()
            return Response(
                {
                    "message": f"총 ({len(serializer.validated_data['penalty_ids'])})개의 Penalty를 성공적으로 삭제했습니다!"  # noqa: E501
                },
                status=status.HTTP_200_OK,
            )


class UpdateMultiPenaltyMixin(mixins.UpdateModelMixin):
    """PenaltyList의 UPDATE 메서드에 사용되는 Mixin.

    단일(dict), 다중(list) request 모두 수용하기 위해 is_many 라는 변수를 사용했습니다.
    """

    def update(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        instances = self.get_objects(request.data if is_many else [request.data])
        serializer = self.get_serializer(
            instances, data=request.data, many=is_many, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def get_objects(self, request_data):
        ids = [item.get("id") for item in request_data]

        return Penalty.objects.filter(id__in=ids)
