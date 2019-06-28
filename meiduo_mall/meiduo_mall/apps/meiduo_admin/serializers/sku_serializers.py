from rest_framework import serializers
from goods.models import SKU,SKUSpecification,GoodsCategory,SPU,SpecificationOption


class SKUSpecModelSerializer(serializers.ModelSerializer):
    spec_id = serializers.IntegerField(read_only=True)
    option_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = SKUSpecification
        fields = ['spec_id','option_id']

# 定义一个序列化器，序列化sku模型类
class SkuSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    category_id = serializers.IntegerField()
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()

    specs = SKUSpecModelSerializer(many=True,read_only=True)

    class Meta:
        model = SKU
        fields = "__all__"

    # 解决编辑一些字段不显示问题
    def create(self, validated_data):
        # 中间表数据
        spec_option = validated_data.pop('spec')

        sku = super().create(validated_data)
        for temp in spec_option:
            temp['sku_id'] = sku.id
            SKUSpecification.objects.create(**temp)

        return sku


    def update(self, instance, validated_data):
        # 更新sku对象的时候，顺带更新中间表数据
        # 1.获得规格及规格选项数据
        spec_option = validated_data.get('spec')
        # 2.根据这些数据，更新中间表
        for temp in spec_option:
            m = SKUSpecification.objects.get(sku_id=instance.id,spec_id=temp['spec_id'])
            m.option_id = temp['option_id']
            m.save()
        return super().update(instance,validated_data)






# 定义GoodsCategory序列化器
class GoodsCategoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = ['id','name']


# 定义spu序列化器
class SpuModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SPU
        fields = ['id','name']

class SpecOptSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationOption
        fields = ['id','value']

# 定义SPUSpecModelSerializer
class SPUSpecModelSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()

    options = SpecOptSerializer(many=True, read_only=True)

    class Meta:
        model = SKUSpecification
        fields = ['id','name','spu','spu_id','options']