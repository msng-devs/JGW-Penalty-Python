# flake8: noqa: F403, F405
# --------------------------------------------------------------------------
# Production용 settings 파일입니다.
#
# 이 파일은 실제 서비스를 운영할 때 사용합니다.
# 실제 서비스를 운영할 때는 이 파일을 사용하고, 로컬에서 개발할 때는 settings_dev.py를 사용합니다.
#
# @author 이준혁(39기) bbbong9@gmail.com
# --------------------------------------------------------------------------
import os

from .base import *


DEBUG = False

ALLOWED_HOSTS = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
