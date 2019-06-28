from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
# 定义一个分页器
class Mypage(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'pagesize'
    page_size = 5
    max_page_size = 10


# 自定义分页器返回格式
    def get_paginated_response(self,data):
        return Response({
            'counts':self.page.paginator.count,
            'lists':data,
            'page':self.page.number,
            'pages':self.page.paginator.num_pages,
            'pagesize':self.page_size,
        })

