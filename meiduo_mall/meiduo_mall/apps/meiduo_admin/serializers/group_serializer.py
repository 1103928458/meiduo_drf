from django.contrib.auth.models import Group,Permission
from rest_framework import serializers

# 定义一个组序列化器
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id','name']


class PerSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id','name']