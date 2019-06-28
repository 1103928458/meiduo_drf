from rest_framework import serializers
from goods.models import SPUSpecification

class SpecSerializer(serializers.ModelSerializer):
    # 规格管理序列化器
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()

    class Meta:
        model = SPUSpecification
        fields = '__all__'