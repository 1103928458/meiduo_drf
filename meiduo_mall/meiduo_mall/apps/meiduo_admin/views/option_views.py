from meiduo_admin.serializers.option_serializer import OptionSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from goods.models import SpecificationOption,SPUSpecification
from meiduo_admin.pages import Mypage
from meiduo_admin.serializers.spec_serializer import SpecSerializer

# 选项管理
class OptionViews(ModelViewSet):
    queryset = SpecificationOption.objects.all()
    serializer_class = OptionSerializer
    pagination_class = Mypage


class SpecSimpleView(ListAPIView):
    queryset = SPUSpecification.objects.all()
    serializer_class = SpecSerializer