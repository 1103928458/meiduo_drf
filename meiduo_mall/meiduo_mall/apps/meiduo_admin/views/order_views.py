from meiduo_admin.serializers.order_serializer import *
from rest_framework.viewsets import ModelViewSet
from meiduo_admin.pages import Mypage
from orders.models import OrderInfo

# 定义一个订单管理的视图
class OrederViewset(ModelViewSet):
    queryset = OrderInfo.objects.all()
    serializer_class = OrderSerializer
    pagination_class = Mypage


    # 搜索过滤
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return self.queryset.filter(order_id__contains=keyword)
        return self.queryset.all()


    def get_serializer_class(self):
        # 根据不同去请求，选用不同的系列化器
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return self.serializer_class

