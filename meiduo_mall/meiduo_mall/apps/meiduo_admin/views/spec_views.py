from meiduo_admin.serializers.spec_serializer import *
from rest_framework.viewsets import ModelViewSet
from meiduo_admin.pages import *

class SpecModelView(ModelViewSet):
    # 规格管理
    queryset = SPUSpecification.objects.all()
    serializer_class = SpecSerializer
    pagination_class = Mypage