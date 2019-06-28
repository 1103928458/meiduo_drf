from goods.models import GoodsVisitCount
from rest_framework import serializers
# 定义一个用来序列化UserVisitCout模型类
# 商品
class GoodsVisitSerializer(serializers.ModelSerializer):
    # category = serializers.PrimaryKeyRelatedField
    category = serializers.StringRelatedField()

    class Meta:
        model = GoodsVisitCount
        fields = ['category','count']