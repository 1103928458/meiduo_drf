from meiduo_admin.pages import Mypage
from rest_framework.viewsets import ModelViewSet
from meiduo_admin.serializers.PermsSerializer import *
from django.contrib.auth.models import Permission,ContentType
from rest_framework.decorators import action
from rest_framework.response import Response

class PermViewSet(ModelViewSet):
    queryset = Permission.objects.order_by("id")
    serializer_class = PermSerializer
    pagination_class = Mypage

    def get_queryset(self):
        if self.action == 'content_types':
            return ContentType.objects.all()
        return self.queryset.all()

    def get_serializer_class(self):
        if self.action == 'content_types':
            return ContentTypeSerializer
        return self.serializer_class

    @action(methods=['get'],detail=False)
    def content_types(self,request):
        content_type = self.get_queryset()
        s = self.get_serializer(content_type,many=True)
        return Response(s.data)



