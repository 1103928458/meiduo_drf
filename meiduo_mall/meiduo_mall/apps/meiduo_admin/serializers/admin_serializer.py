from rest_framework import serializers
from users.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'mobile',

            'password',
            'groups',
            'user_permissions'
        ]

        extra_kwargs = {
            'password':{'write_only':True},
            'groups':{'write_only':True},
            'user_permissions':{'write_only':True},
        }

    def create(self, validated_data):
        validated_data['password'] = make_password('password')
        validated_data['is_staff'] = True
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 判断有没有传入密码，如果有密码就进行加密，没有就返回以前的密码
        password = validated_data.get('password')
        if password:
            validated_data['password'] = make_password('password')

        else:
            validated_data['password'] = instance.password

        return super().update(instance,validated_data)


class AdminGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id','name']