# --------------------------------------------------------------------------
# Penalty Application의 Views를 정의한 모듈입니다.
#
# @author 이준혁(39기) bbbong9@gmail.com
# --------------------------------------------------------------------------
import logging

from rest_framework import generics, mixins

from core import permissions
from core.permissions import IsAdminOrSelf

from apps.penalty.models import Penalty
from apps.serializers import (
    PenaltyAddRequestSerializer,
    PenaltyBulkDeleteRequestSerializer,
    PenaltyIdSerializer,
    PenaltyResponseSerializer,
    PenaltyUpdateRequestSerializer,
)
from apps.utils import filters, decorators
from apps.utils import documentation as docs
from apps.utils.paginations import CustomBasePagination

from . import mixins as penalty_mixins

logger = logging.getLogger("django")


class PenaltyDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Penalty API

    ---
    Penalty를 조회하고, 삭제하고, 수정하는 API를 제공합니다.

    * @author 이준혁(39기) bbbong9@gmail.com
    """

    queryset = Penalty.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "penaltyId"
    permission_classes = [IsAdminOrSelf]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PenaltyResponseSerializer
        elif self.request.method == "PUT":
            return PenaltyUpdateRequestSerializer
        return PenaltyIdSerializer

    def perform_destroy(self, instance):
        uid, role_id = permissions.get_auth_header(self.request)
        permissions.check_permission(uid=uid, role_id=role_id)
        message = f"User {uid} deleted penalty with id {instance.id}"
        logger.info(message)
        instance.delete()

    def perform_update(self, serializer):
        uid, role_id = permissions.get_auth_header(self.request)
        permissions.check_permission(uid=uid, role_id=role_id)
        serializer.save(uid=uid)
        message = f"User {uid} updated penalty with id {serializer.instance.id}"
        logger.info(message)

    @decorators.methods_swagger_decorator
    def get(self, request, *args, **kwargs):
        """
        단일 penalty를 조회

        ---
        RBAC - 2 이상
        """
        return self.retrieve(request, *args, **kwargs)

    @decorators.methods_swagger_decorator
    def put(self, request, *args, **kwargs):
        """
        단일 penalty를 업데이트

        ---
        RBAC - 4(어드민)

        부분 업데이트를 지원합니다.
        """
        return self.update(request, *args, **kwargs, partial=True)

    @decorators.methods_swagger_decorator
    def delete(self, request, *args, **kwargs):
        """
        단일 penalty를 제거

        ---
        RBAC - 4(어드민)
        """
        return self.destroy(request, *args, **kwargs)


class PenaltyList(
    mixins.ListModelMixin,
    penalty_mixins.CreateMultiPenaltyMixin,
    penalty_mixins.DestroyMultiPenaltyMixin,
    penalty_mixins.UpdateMultiPenaltyMixin,
    generics.GenericAPIView,
):
    """
    Penalty API

    ---
    penalty를 등록

    * @author 이준혁(39기) bbbong9@gmail.com
    """

    queryset = Penalty.objects.all().order_by("-id")
    pagination_class = CustomBasePagination
    filterset_class = filters.PenaltyFilter
    permission_classes = [IsAdminOrSelf]

    def get_serializer_class(self):
        if self.request.method == "DELETE":
            return PenaltyBulkDeleteRequestSerializer
        elif self.request.method == "PUT":
            return PenaltyUpdateRequestSerializer
        elif self.request.method == "POST":
            return PenaltyAddRequestSerializer
        return PenaltyResponseSerializer

    @decorators.common_swagger_decorator
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @decorators.methods_swagger_decorator
    def post(self, request, *args, **kwargs):
        """
        penalty를 등록

        ---
        RBAC - 4(어드민)
        """
        return self.create(request, *args, **kwargs)

    @decorators.methods_swagger_decorator
    def put(self, request, *args, **kwargs):
        """
        다수 penalty를 업데이트

        ---
        RBAC - 4(어드민)

        부분 업데이트를 지원합니다.
        """
        return self.update(request, *args, **kwargs)

    @decorators.methods_swagger_decorator
    def delete(self, request, *args, **kwargs):
        """
        다수 penalty를 제거

        ---
        RBAC - 4(어드민)
        """
        return self.destroy(request, *args, **kwargs)


PenaltyList.__doc__ = docs.get_penalty_doc()
