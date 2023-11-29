# --------------------------------------------------------------------------
# 서비스에 사용되는 Base Models를 정의한 모듈입니다.
#
# :class Role: RBAC를 위해 사용되며, 권한을 정의합니다.
# :class Member: RBAC를 위해 사용되며, 회원을 정의합니다.
#
# @author 이준혁(39기) bbbong9@gmail.com
# --------------------------------------------------------------------------
from django.db import models
from django.utils import timezone


class Role(models.Model):
    # 해당 권한의 ID(PK)
    id = models.AutoField(primary_key=True)

    # 해당 권한의 명칭("ROLE_" 시작하는 대문자)
    name = models.CharField(max_length=45, null=False, unique=True)

    class Meta:
        db_table = "ROLE"
        verbose_name = "Role"
        verbose_name_plural = "Roles"


class Member(models.Model):
    # 해당 회원의 UID(Firebase uid) (PK)
    id = models.CharField(max_length=28, primary_key=True)

    # 회원의 실명
    name = models.CharField(max_length=45, null=False)

    # 회원의 이메일
    email = models.EmailField(max_length=255, null=False, unique=True)

    # 회원의 권한 레벨
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=False)

    # 회원의 활동 상태
    status = models.BooleanField(default=True)

    class Meta:
        db_table = "MEMBER"
        verbose_name = "Member"
        verbose_name_plural = "Members"
