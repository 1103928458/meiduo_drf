
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import action
from users.models import User
from datetime import timedelta


class HomeView(ViewSet):
    """用户总数"""
    @action(methods=['get'],detail=False)
    def total_count(self,request):

        count = User.objects.filter(is_active=True).count()
        date = timezone.now().date()

        return Response({
            'count':count,
            'date':date
        })

    @action(methods=['get'],detail=False)
    # 日增用户统计
    def day_increment(self,request):
        # 1.获得当日日期
        date = timezone.now()
        # 2.过滤出当天新建用户数量
        count  = User.objects.filter(date_joined__gte=date.replace(hour=0,minute=0,second=0)-timedelta(hours=8,minutes=6,seconds=0)).count()
        # 3. 返回数据
        return Response({
            'count':count,
            'date':date.date()
        })
