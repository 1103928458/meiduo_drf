from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView,CreateAPIView
from users.models import User
from meiduo_admin.serializers.user_serializers import *
from meiduo_admin.pages import *


class UserView(ListAPIView,CreateAPIView):
    # 用户管理
    queryset = User.objects.all()
    serializer_class = UserModelSerializer

    # 配置分页器
    pagination_class = Mypage


    # 搜索：自定义获得数据集
    def get_queryset(self):
        # 判断字符串中有没有keyword这个值
        keyword = self.request.query_params.get('keyword')

        if keyword:
            return self.queryset.filter(username__contains=keyword)

        return self.queryset.all()  # 如果没有就全部返回



    # def get(self,request):
        # 获得数据集
        # user_queryset = self.get_queryset()
        # # 对该数据集进行分页处理，得到一个子集
        # page = self.paginate_queryset(user_queryset)
        # # # 获得序序列化器
        # # serializer = self.get_serializer(user_queryset,many=True)
        # # # 返回
        # # return Response(serializer.data)
        # # 对该子集进行序列化处理
        # if page:
        #     page_serializer = self.get_serializer(page,many=True)
        #     return self.get_paginated_response(page_serializer.data)
        #
        # # 如果分页不成功就将数据全部返回
        # serializer = self.get_serializer(user_queryset,many=True)
        # return Response(serializer.data)
