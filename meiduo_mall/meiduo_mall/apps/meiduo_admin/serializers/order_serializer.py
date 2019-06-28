from rest_framework import serializers
from orders.models import OrderInfo,OrderGoods
from goods.models import SKU




class OrderSerializer(serializers.ModelSerializer):
    # 定义一个订单管理序列化器
    class Meta:
        model = OrderInfo
        fields = ['order_id', 'create_time','status']

        extra_kwargs = {
            'order_id':{'read_only':True},
            'status':{'required':True}

        }

class SKUSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ['name','default_image']

class orderGoodsSerializer(serializers.ModelSerializer):
    sku = SKUSimpleSerializer( read_only=True)
    class Meta:
        model = OrderGoods
        fields = ['count','price','sku']


class OrderDetailSerializer(serializers.ModelSerializer):
    skus = orderGoodsSerializer(many=True)
    user = serializers.StringRelatedField()
    # 订单详情
    class Meta:
        model = OrderInfo
        fields = '__all__'