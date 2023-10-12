# flake8: noqa: F403, F405
# --------------------------------------------------------------------------
# Dev용 settings 파일입니다.
#
# 이 파일은 로컬에서 개발할 때 사용합니다.
# 테스트케이스 실행 및 테스트 서버 실행 시, 다음 명령어로 이 세팅을 적용할 수 있습니다.
#  - python manage.py <명령어> --settings=jgw_attendance.settings.settings_dev
#
# @author 이준혁(39기) bbbong9@gmail.com
# --------------------------------------------------------------------------
import os

from .base import *


DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "JGWPenaltyDBdev",
        "USER": "bnbong",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": "3306",
    }
}
