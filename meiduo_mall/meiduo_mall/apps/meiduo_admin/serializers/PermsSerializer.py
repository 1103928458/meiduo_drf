from django.contrib.auth.models import Permission,ContentType
from rest_framework import serializers


class PermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = [
            'id',
            'name',
            'codename',
            'content_type'
        ]

class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['id','name']