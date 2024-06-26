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
from apps.utils.paginations import CustomBasePagination
from apps.utils import filters

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

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs, partial=True)

    def delete(self, request, *args, **kwargs):
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
    다수 penalty를 조회, 등록, 수정, 삭제하는 API를 제공합니다.

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

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
