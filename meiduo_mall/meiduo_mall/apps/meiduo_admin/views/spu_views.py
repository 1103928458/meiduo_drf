
from meiduo_admin.serializers.spu_serializers import *
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from meiduo_admin.pages import Mypage

class SpuView(ModelViewSet):
    serializer_class = SPUModelSerializer
    queryset = SPU.objects.all()
    pagination_class = Mypage


class BrandViews(ListAPIView):
    serializer_class = BrandModelSerializer
    queryset = Brand.objects.all()


# 获得一级分类所有数据的接口
class GoodsCategoryView(ListAPIView):
    queryset = GoodsCategory.objects.all()
    serializer_class = GoodCategoryserializer

    def get_queryset(self):
        parent_id = self.kwargs.get("pk")

        if parent_id:
            return self.queryset.filter(parent_id=parent_id)

        return self.queryset.filter(parent_id=None)