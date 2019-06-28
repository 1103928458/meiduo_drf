from goods.models import SpecificationOption
from rest_framework import serializers

class OptionSerializer(serializers.ModelSerializer):
    #规格选项管理
    spec = serializers.StringRelatedField()
    spec_id = serializers.IntegerField()

    class Meta:
        model = SpecificationOption
        fields = ['id','value','spec','spec_id']