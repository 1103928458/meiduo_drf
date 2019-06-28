from rest_framework import serializers
from goods.models import SKUImage,SKU
from fdfs_client.client import Fdfs_client
from django.conf import settings
# 定义图片管理序列化器

class SkuimageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKUImage
        fields = ['id','sku','image']

    def create(self, validated_data):
        image = validated_data.pop('image')
        conn = Fdfs_client(settings.FDFS_CONFIG_PATH)
        content = image.read()
        result = conn.upload_by_buffer(content)
        if not result.get('Status') == 'Upload successed.':
            raise serializers.ValidationError('上传失败')
        url = result.get('Remote file_id')
        validated_data['image'] = url
        return super().create(validated_data)


    def update(self, instance, validated_data):
        # 更新图片
        image = validated_data.pop('image')
        conn = Fdfs_client(settings.FDFS_CONFIG_PATH)
        connet  =image.read()
        result = conn.upload_by_buffer(connet)
        if not result.get('Status') == 'Upload successed.':
            raise serializers.ValidationError('上传失败')

        url = result.get('Remote file_id')
        instance.image = url
        instance.save()
        return instance


class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ['id','name']