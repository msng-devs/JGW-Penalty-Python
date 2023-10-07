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
    # TODO: 단일 penalty 추가할 때, request body type가 list 혹은 단일인지 구분하는 로직 추가
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # message = {"message": f"총 ({len(serializer.data)})개의 Penalty를 성공적으로 추가했습니다!"}
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        # print("create performed")
        # print(serializer.validated_data)
        penalties = serializer.save()
        for penalty in penalties:
            message = (
                f"User {penalty.target_member_id} added penalty with ID {penalty.id}"
            )
            logger.info(message)


class DestroyMultiPenaltyMixin(mixins.DestroyModelMixin):
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
    def update(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        instances = self.get_objects(request.data if is_many else [request.data])
        serializer = self.get_serializer(
            instances, data=request.data, many=is_many, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            # {"message": f"총 ({len(serializer.data)})개의 Penalty를 성공적으로 업데이트 했습니다!"},
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def get_objects(self, request_data):
        # Extract IDs from the request data
        ids = [item.get("id") for item in request_data]

        # Fetch Penalty objects based on the given IDs
        return Penalty.objects.filter(id__in=ids)
