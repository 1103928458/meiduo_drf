from meiduo_admin.serializers.admin_serializer import *
from rest_framework.viewsets import ModelViewSet
from users.models import User
from meiduo_admin.pages import Mypage
from rest_framework.response import Response
from rest_framework.decorators import action

class AdminViewset(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminSerializer
    pagination_class = Mypage

    @action(['get'],detail=False)
    def simple(self,request):
        groups = Group.objects.all()
        s = AdminGroupSerializer(groups,many=True)
        return Response(s.data)
