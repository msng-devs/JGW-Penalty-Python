# --------------------------------------------------------------------------
# Log message formatter에 ANSI 이스케이프 시퀀스 제거하는 모듈입니다.
#
# @author 이준혁(39기) bbbong9@gmail.com
# --------------------------------------------------------------------------
import re
import logging


class NoColorFormatter(logging.Formatter):
    def format(self, record):
        message = super().format(record)
        return re.sub(r'\x1b\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]', '', message)
