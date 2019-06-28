from rest_framework.viewsets import ModelViewSet
from meiduo_admin.serializers.group_serializer import *
from meiduo_admin.pages import Mypage
from django.contrib.auth.models import Group,Permission
from rest_framework.decorators import action
from rest_framework.response import Response
# 定义一个组视图
class GroupViewset(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = Mypage

    @action(['get'],detail=False)
    def permission_simple(self,request):
        perms = Permission.objects.all()
        s = PerSimpleSerializer(perms,many=True)
        return Response(s.data)