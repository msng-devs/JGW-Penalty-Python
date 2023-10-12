# --------------------------------------------------------------------------
# 페이지네이션을 구현하기 위한 모듈입니다.
#
# Penalty 서비스 중 CustomBasePagination을 상속받는 모든 클래스는
# 쿼리파라미터에 page, page_size를 명시하여 페이지에 표현되는 데이터의 개수를
# 조절할 수 있습니다.
#
# @author 이준혁(39기) bbbong9@gmail.com
# --------------------------------------------------------------------------
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from collections import OrderedDict

from . import constants


class CustomBasePagination(PageNumberPagination):
    page_size = constants.DEFAULT_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = constants.MAX_PAGE_SIZE

    def get_paginated_response(self, data):
        previous = self.get_previous_link()
        if previous is not None:
            query = {
                k: v
                for k, v in list(
                    map(lambda x: x.split("="), previous.split("?")[1].split("&"))
                )
            }
            if "page" not in query:
                query["page"] = "1"
                query = sorted(query.items(), key=lambda x: x[0])
                previous = (
                    previous.split("?")[0]
                    + "?"
                    + "&".join([f"{i[0]}={i[1]}" for i in query])
                )

        return Response(
            OrderedDict(
                [
                    ("count", len(data)),
                    ("total_pages", self.page.paginator.num_pages),
                    ("next", self.get_next_link()),
                    ("previous", previous),
                    ("results", data),
                ]
            )
        )
