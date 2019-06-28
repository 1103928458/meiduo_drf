from meiduo_admin.serializers.sku_serializers import SkuSerializer
from rest_framework.generics import ListAPIView,DestroyAPIView,CreateAPIView
from goods.models import *
from meiduo_admin.pages import *
from goods.models import GoodsCategory
from meiduo_admin.serializers.sku_serializers import *
from rest_framework.viewsets import ModelViewSet

class SKUViews(ModelViewSet):
    queryset = SKU.objects.all()
    serializer_class = SkuSerializer
    pagination_class = Mypage


    # 过滤商品进行搜索
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return self.queryset.filter(name__contains=keyword)

        return self.queryset.all()



class GoodsCategoryViews(ListAPIView):
    serializer_class = GoodsCategoryModelSerializer
    queryset = GoodsCategory.objects.filter(parent_id__gte=37)


class SpuViews(ListAPIView):
    serializer_class = SpuModelSerializer
    queryset = SPU.objects.all()


class SpecOptView(ListAPIView):
    queryset = SpecificationOption.objects.all()
    serializer_class = SKUSpecModelSerializer

    def get_queryset(self):
        spu_id = self.kwargs.get('pk')
        return self.queryset.filter(pk=spu_id)
