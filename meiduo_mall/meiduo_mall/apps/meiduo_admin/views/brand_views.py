from meiduo_admin.serializers.brand_serializer import *
from rest_framework.viewsets import ModelViewSet
from meiduo_admin.pages import Mypage
from goods.models import Brand

# 定义品牌视图
class BrandSViewset(ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    pagination_class = Mypage
