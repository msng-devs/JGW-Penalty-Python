# --------------------------------------------------------------------------
# 유저 권한을 확인하는 모듈 입니다.
#
# @author 이준혁(39기) bbbong9@gmail.com
# --------------------------------------------------------------------------
from django.utils.six import text_type

from rest_framework import HTTP_HEADER_ENCODING
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from apps.common.models import Role

VALID_ROLES = [
    1,  # "ROLE_GUEST",
    2,  # "ROLE_USER0",
    3,  # "ROLE_USER1",
    4,  # "ROLE_ADMIN",
    5,  # "ROLE_DEV"
]


def get_auth_header(request):
    uid = request.META.get("HTTP_USER_PK")
    role_id = request.META.get("HTTP_ROLE_PK")

    if isinstance(uid, text_type) and isinstance(role_id, text_type):
        uid = uid.encode(HTTP_HEADER_ENCODING)
        role_id = role_id.encode(HTTP_HEADER_ENCODING)

    # uid와 role_id가 헤더에 포함되어 있는지 확인
    if uid is None or role_id is None:
        raise PermissionDenied("유저 인증 정보가 없습니다.")

    return uid, int(role_id)


def check_permission(uid, role_id, target_member_id=None):
    try:
        admin_role_id = Role.objects.get(name="ROLE_ADMIN").id

        # 해당 유저의 role을 가져와 권한 확인
        if role_id < admin_role_id:
            if not target_member_id or uid != target_member_id:
                raise PermissionDenied("해당 계정은 이 작업을 수행할 권한이 없습니다.")

    except Role.DoesNotExist:
        raise IndexError("Admin role not found.")


class IsAdminOrSelf(BasePermission):
    message = "이 작업을 수행할 권한이 없습니다."

    def has_permission(self, request, view):
        uid, role_id = get_auth_header(request)

        # role_id가 유효한지 확인
        if role_id not in VALID_ROLES:
            raise PermissionDenied("유효하지 않은 권한입니다.")

        request.uid = uid
        request.role_id = role_id

        target_member_id = request.query_params.get("targetMember", None)

        penalty_id = view.kwargs.get("penaltyId", None)

        if request.method == "GET" and penalty_id:
            penalty = view.get_object()
            if uid == penalty.target_member_id:
                return True

        return self.check_permission(uid, role_id, target_member_id)

    @staticmethod
    def check_permission(uid, role_id, target_member_id=None):
        try:
            admin_role_id = Role.objects.get(name="ROLE_ADMIN").id

            # 해당 유저의 role을 가져와 권한 확인
            if role_id < admin_role_id:  # Admin 유저인지 확인
                if (
                    not target_member_id or uid != target_member_id
                ):  # Admin이 아니라면 자기 자신인지 확인
                    raise PermissionDenied("해당 계정은 이 작업을 수행할 권한이 없습니다.")

            return True  # 권한이 충족되면 True 반환

        except Role.DoesNotExist:
            raise IndexError("Admin role not found.")


class IsProbationaryMember(BasePermission):
    message = "이 작업을 수행할 권한이 없습니다."

    def has_permission(self, request, view):
        uid, role_id = get_auth_header(request)

        # role_id가 2 이상인지 확인
        if role_id < 2:
            raise PermissionDenied("유효하지 않은 권한입니다.")

        request.uid = uid
        request.role_id = role_id

        return True


class IsUser(BasePermission):
    message = "이 작업을 수행할 권한이 없습니다."

    def has_permission(self, request, view):
        uid, role_id = get_auth_header(request)

        request.uid = uid
        request.role_id = role_id

        return True
