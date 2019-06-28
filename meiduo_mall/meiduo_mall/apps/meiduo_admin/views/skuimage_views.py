from rest_framework.viewsets import ModelViewSet
from  meiduo_admin.serializers.skuimage_serializer import *
from goods.models import SKUImage
from meiduo_admin.pages import Mypage
# 定义一个图片管理视图
class SkuimageViewset(ModelViewSet):
    queryset = SKUImage.objects.all()
    serializer_class = SkuimageSerializer
    pagination_class = Mypage


class SKUViewset(ModelViewSet):
    queryset = SKU.objects.all()
    serializer_class = SKUSerializer