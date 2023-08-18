from django.http import JsonResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.member.models import Member
from apps.role.models import Role
from apps.penalty.models import Penalty
from apps.serializers import (
    PenaltyAddRequestSerializer,
    PenaltyBulkDeleteRequestSerializer,
    PenaltyIdSerializer,
    PenaltyResponseSerializer,
    PenaltyUpdateRequestSerializer,
)


class AddPenalty(APIView):
    def post(self, request):
        uid = request.META.get("HTTP_USER_PK")
        role_id = request.META.get("HTTP_ROLE_PK")

        serializer = PenaltyAddRequestSerializer(data=request.data, many=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": f"총 {len(serializer.data)}개의 Penalty를 성공적으로 추가했습니다!"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PenaltyDetail(APIView):
    def get(self, request, penaltyId):
        uid = request.META.get("HTTP_USER_PK")
        role_id = request.META.get("HTTP_ROLE_PK")

        penalty = Penalty.objects.get(id=penaltyId)
        serializer = PenaltyResponseSerializer(penalty)

        # Role 모델을 사용하여 관리자 Role의 ID 조회
        admin_role = Role.objects.get(name="ROLE_ADMIN")
        admin_role_id = admin_role.id

        # 권한 및 타겟 멤버 확인
        if role_id < admin_role_id and uid != str(serializer.data["target_member_id"]):
            raise PermissionDenied("FORBIDDEN_ROLE")

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, penaltyId):
        uid = request.META.get("HTTP_USER_PK")
        role_id = request.META.get("HTTP_ROLE_PK")

        penalty = Penalty.objects.get(id=penaltyId)
        penalty.delete()
        serializer = PenaltyIdSerializer({"id": penaltyId})

        # Role 모델을 사용하여 관리자 Role의 ID 조회
        admin_role = Role.objects.get(name="ROLE_ADMIN")
        admin_role_id = admin_role.id

        # 권한 및 타겟 멤버 확인
        if role_id < admin_role_id and uid != str(serializer.data["target_member_id"]):
            raise PermissionDenied("FORBIDDEN_ROLE")

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, penaltyId):
        uid = request.META.get("HTTP_USER_PK")
        role_id = request.META.get("HTTP_ROLE_PK")

        penalty = Penalty.objects.get(id=penaltyId)
        serializer = PenaltyUpdateRequestSerializer(penalty, data=request.data)

        # Role 모델을 사용하여 관리자 Role의 ID 조회
        admin_role = Role.objects.get(name="ROLE_ADMIN")
        admin_role_id = admin_role.id

        # 권한 및 타겟 멤버 확인
        if role_id < admin_role_id and uid != str(serializer.data["target_member_id"]):
            raise PermissionDenied("FORBIDDEN_ROLE")

        if serializer.is_valid():
            serializer.save(uid=uid)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PenaltyList(APIView):
    def get(self, request):
        uid = request.META.get("HTTP_USER_PK")
        role_id = request.META.get("HTTP_ROLE_PK")

        penalties = Penalty.objects.all()
        serializer = PenaltyResponseSerializer(penalties, many=True)

        # Role 모델을 사용하여 관리자 Role의 ID 조회
        admin_role = Role.objects.get(name="ROLE_ADMIN")
        admin_role_id = admin_role.id

        # 권한 및 타겟 멤버 확인
        if role_id < admin_role_id and uid != str(serializer.data["target_member_id"]):
            raise PermissionDenied("FORBIDDEN_ROLE")

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        uid = request.META.get("HTTP_USER_PK")
        role_id = request.META.get("HTTP_ROLE_PK")

        serializer = PenaltyBulkDeleteRequestSerializer(data=request.data)

        # Role 모델을 사용하여 관리자 Role의 ID 조회
        admin_role = Role.objects.get(name="ROLE_ADMIN")
        admin_role_id = admin_role.id

        # 권한 및 타겟 멤버 확인
        if role_id < admin_role_id and uid != str(serializer.data["target_member_id"]):
            raise PermissionDenied("FORBIDDEN_ROLE")

        if serializer.is_valid():
            serializer.delete()

            return Response(
                {
                    "message": f"총 {len(serializer.validated_data['penalty_ids'])}개의 Penalty를 성공적으로 삭제했습니다!"
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        uid = request.META.get("HTTP_USER_PK")
        role_id = request.META.get("HTTP_ROLE_PK")

        serializer = PenaltyUpdateRequestSerializer(data=request.data, many=True)

        # Role 모델을 사용하여 관리자 Role의 ID 조회
        admin_role = Role.objects.get(name="ROLE_ADMIN")
        admin_role_id = admin_role.id

        # 권한 및 타겟 멤버 확인
        if role_id < admin_role_id and uid != str(serializer.data["target_member_id"]):
            raise PermissionDenied("FORBIDDEN_ROLE")

        if serializer.is_valid():
            for item in serializer.validated_data:
                penalty = Penalty.objects.get(id=item["id"])
                serializer.update(penalty, item)

            return Response(
                {
                    "message": f"총 {len(serializer.validated_data)}개의 Penalty를 성공적으로 업데이트 했습니다!"
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
