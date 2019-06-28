from rest_framework.viewsets import ModelViewSet
from meiduo_admin.serializers.channel_serializer import *
from goods.models import GoodsChannel,GoodsChannelGroup,GoodsCategory
from meiduo_admin.pages import Mypage


# 频道视图
class ChannelViewSet(ModelViewSet):
    queryset = GoodsChannel.objects.all()
    serializer_class = ChannelSerializer
    pagination_class = Mypage


class GoodsChannelGroupViewset(ModelViewSet):
    queryset = GoodsChannelGroup.objects.all()
    serializer_class = GoodsChannelGroupSerializer

class GoodsCategoryViewset(ModelViewSet):
    queryset = GoodsCategory.objects.filter(parent=None)
    serializer_class = GoodCategorySerializer
