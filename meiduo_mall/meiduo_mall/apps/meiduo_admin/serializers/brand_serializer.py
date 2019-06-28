from fdfs_client.client import Fdfs_client
from rest_framework import serializers
from goods.models import Brand
from django.conf import settings
# 序列化品牌管理操作
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id','name','logo',"first_letter"]

    def create(self, validated_data):
        logo = validated_data['logo']

        # 1.获得fdfs链接对象
        conn = Fdfs_client(settings.FDFS_CONFIG_PATH)
        # 2.上传文件
        content = logo.read()
        result = conn.upload_by_buffer(content)
        # 3.判断是否上传成功
        if not result.get('Status')=='Upload successed.':
            raise serializers.ValidationError('上传失败')
        # 4.如果成功，获得fdfs文件标示
        url = result.get('Remote file_id')
        # 5.更新当前品牌对象logo字段
        validated_data['logo'] = url
        return super().create(validated_data)


    def update(self, instance, validated_data):
        # 更新图片
        logo = validated_data.pop('logo')     # 得到最新上传图片
        conn = Fdfs_client(settings.FDFS_CONFIG_PATH)   # 链接fdfs
        connet = logo.read()  # 上传图片
        result = conn.upload_by_buffer(connet)
        if not result.get('Status') == 'Upload successed.':
            raise serializers.ValidationError('上传失败')
        url = result.get('Remote file_id')
        instance.logo = url
        instance.save()
        return instance