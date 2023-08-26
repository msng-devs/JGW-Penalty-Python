from django.utils.six import text_type
from django.core.paginator import Paginator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework import status, HTTP_HEADER_ENCODING

from apps.role.models import Role
from apps.penalty.models import Penalty
from apps.serializers import (
    PenaltyAddRequestSerializer,
    PenaltyBulkDeleteRequestSerializer,
    PenaltyIdSerializer,
    PenaltyResponseSerializer,
    PenaltyUpdateRequestSerializer,
)


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
            serializer.save()
            return Response(
                {"message": f"총 ({len(serializer.data)})개의 Penalty를 성공적으로 추가했습니다!"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PenaltyDetail(APIView):
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

        penalty = Penalty.objects.get(id=penaltyId)
        penalty.delete()
        serializer = PenaltyIdSerializer({"id": penaltyId})

        # request를 보낸 유저의 권한 확인
        check_permission(
            uid=uid,
            role_id=role_id,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, penaltyId):
        uid, role_id = get_auth_header(request)

        penalty = Penalty.objects.get(id=penaltyId)
        serializer = PenaltyUpdateRequestSerializer(penalty, data=request.data)

        # request를 보낸 유저의 권한 확인
        check_permission(
            uid=uid,
            role_id=role_id,
        )

        if serializer.is_valid():
            serializer.save(uid=uid)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PenaltyList(APIView):
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

        serializer = PenaltyBulkDeleteRequestSerializer(data=request.data)

        # request를 보낸 유저의 권한 확인
        check_permission(
            uid=uid,
            role_id=role_id,
        )

        if serializer.is_valid():
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

        # many = True 일 시, PenaltyBulkUpdateRequestSerializer의 update 메서드가 호출됨
        serializer = PenaltyUpdateRequestSerializer(data=request.data, many=True)

        # request를 보낸 유저의 권한 확인
        check_permission(
            uid=uid,
            role_id=role_id,
        )

        if serializer.is_valid():
            serializer.update(
                Penalty.objects.filter(
                    id__in=[item["id"] for item in serializer.validated_data]
                ),
                serializer.validated_data,
            )

            return Response(
                {
                    "message": f"총 ({len(serializer.validated_data)})개의 Penalty를 성공적으로 업데이트 했습니다!"
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
