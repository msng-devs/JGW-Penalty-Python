from django.db import models


class Role(models.Model):
    # 해당 권한의 ID(PK)
    id = models.AutoField(primary_key=True)

    # 해당 권한의 명칭("ROLE_" 시작하는 대문자)
    name = models.CharField(max_length=45, null=False, unique=True)
