import logging

from django.utils.six import text_type
from django.core.paginator import Paginator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework import status, HTTP_HEADER_ENCODING

from apps.common.models import Role
from apps.penalty.models import Penalty
from apps.serializers import (
    PenaltyAddRequestSerializer,
    PenaltyBulkDeleteRequestSerializer,
    PenaltyIdSerializer,
    PenaltyResponseSerializer,
    PenaltyUpdateRequestSerializer,
)

logger = logging.getLogger("django")


def get_auth_header(request):
    uid = request.META.get("HTTP_USER_PK", b"")
    role_id = request.META.get("HTTP_ROLE_PK", b"")

    if isinstance(uid, text_type) and isinstance(role_id, text_type):
        uid = uid.encode(HTTP_HEADER_ENCODING)
        role_id = role_id.encode(HTTP_HEADER_ENCODING)

    return uid, role_id


def check_permission(uid, role_id, target_member_id=None):
    # Role 모델을 사용하여 관리자 Role의 ID 조회
    admin_role = Role.objects.get(name="ROLE_ADMIN")
    admin_role_id = admin_role.id

    # 해당 유저의 role을 가져와 권한 확인
    if role_id < admin_role_id:
        if not target_member_id or uid != target_member_id:
            raise PermissionDenied("FORBIDDEN_ROLE")


class AddPenalty(APIView):
    """
    신규 Penalty 추가

    ---
    RBAC - 4(어드민)

    해당 API를 통해 신규 Penalty를 추가할 수 있습니다.

    * @author 이준혁(39기) bbbong9@gmail.com
    """

    def post(self, request):
        uid, role_id = get_auth_header(request)

        serializer = PenaltyAddRequestSerializer(data=request.data, many=True)

        if serializer.is_valid():
            # request를 보낸 유저의 권한 확인
            check_permission(
                uid=uid,
                target_member_id=str(serializer.data[0]["target_member_id"]),
                role_id=role_id,
            )
            penalties = serializer.save()

            for penalty in penalties:
                message = f"User {uid} added penalty with ID {penalty.id}"
                logger.info(message)

            return Response(
                {"message": f"총 ({len(serializer.data)})개의 Penalty를 성공적으로 추가했습니다!"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PenaltyDetail(APIView):
    """
    Penalty API

    ---
    Penalty를 조회하고, 삭제하고, 수정하는 API를 제공합니다.

    * @author 이준혁(39기) bbbong9@gmail.com
    """

    def get(self, request, penaltyId):
        uid, role_id = get_auth_header(request)

        penalty = Penalty.objects.get(id=penaltyId)
        serializer = PenaltyResponseSerializer(penalty)

        # request를 보낸 유저의 권한 확인
        check_permission(
            uid=uid,
            target_member_id=str(serializer.data["target_member_id"]),
            role_id=role_id,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, penaltyId):
        uid, role_id = get_auth_header(request)

        # request를 보낸 유저의 권한 확인
        check_permission(
            uid=uid,
            role_id=role_id,
        )

        penalty = Penalty.objects.get(id=penaltyId)
        penalty.delete()
        serializer = PenaltyIdSerializer({"id": penaltyId})

        message = f"User {uid} deleted penalty with id {penaltyId}"
        logger.info(message)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, penaltyId):
        uid, role_id = get_auth_header(request)

        # request를 보낸 유저의 권한 확인
        check_permission(
            uid=uid,
            role_id=role_id,
        )

        penalty = Penalty.objects.get(id=penaltyId)
        serializer = PenaltyUpdateRequestSerializer(penalty, data=request.data)

        if serializer.is_valid():
            serializer.save(uid=uid)
            message = f"User {uid} updated penalty with id {penaltyId}"
            logger.info(message)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PenaltyList(APIView):
    """
    Penalty API

    ---
    penalty를 등록

    * @author 이준혁(39기) bbbong9@gmail.com
    """

    def get(self, request):
        uid, role_id = get_auth_header(request)

        # 기본 값 설정
        default_limit = 1000
        default_page = 0
        default_sort = "-created_date"

        # 쿼리 파라미터에서 limit, page, sort 값을 가져옴
        limit = int(request.GET.get("limit", default_limit))
        page = int(request.GET.get("page", default_page))
        sort = request.GET.get("sort", default_sort)

        # 관리자 Role의 ID 조회
        admin_role = Role.objects.get(name="ROLE_ADMIN")
        admin_role_id = admin_role.id

        # 권한 및 타겟 멤버 확인
        target_member_query = request.GET.get("targetMember", None)
        if role_id < admin_role_id and (
            not target_member_query or target_member_query != uid
        ):
            raise PermissionDenied("FORBIDDEN_ROLE")

        penalties = Penalty.objects.all().order_by(sort)
        if target_member_query:
            penalties = penalties.filter(target_member_id=target_member_query)

        # 페이지네이션
        paginator = Paginator(penalties, limit)
        current_page_penalties = paginator.get_page(page)
        serializer = PenaltyResponseSerializer(current_page_penalties, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        uid, role_id = get_auth_header(request)

        # request를 보낸 유저의 권한 확인
        check_permission(
            uid=uid,
            role_id=role_id,
        )

        serializer = PenaltyBulkDeleteRequestSerializer(data=request.data)

        if serializer.is_valid():
            penalties_to_delete = Penalty.objects.filter(
                id__in=serializer.validated_data["penalty_ids"]
            )

            for penalty in penalties_to_delete:
                message = f"User {uid} deleted penalty with ID {penalty.id}"
                logger.info(message)

            serializer.delete()

            return Response(
                {
                    "message": f"총 ({len(serializer.validated_data['penalty_ids'])})개의 Penalty를 성공적으로 삭제했습니다!"
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        uid, role_id = get_auth_header(request)

        # request를 보낸 유저의 권한 확인
        check_permission(
            uid=uid,
            role_id=role_id,
        )

        # many = True 일 시, PenaltyBulkUpdateRequestSerializer의 update 메서드가 호출됨
        serializer = PenaltyUpdateRequestSerializer(data=request.data, many=True)

        if serializer.is_valid():
            updated_penalties = Penalty.objects.filter(
                id__in=[item["id"] for item in serializer.validated_data]
            )

            serializer.update(updated_penalties, serializer.validated_data)

            for penalty in updated_penalties:
                message = f"User {uid} updated penalty with ID {penalty.id}"
                logger.info(message)

            return Response(
                {
                    "message": f"총 ({len(serializer.validated_data)})개의 Penalty를 성공적으로 업데이트 했습니다!"
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
