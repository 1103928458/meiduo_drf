
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import action
from users.models import User
from orders.models import OrderInfo
from datetime import timedelta
import pytz
from django.conf import settings
from meiduo_admin.serializers.home_serializers import *
from rest_framework.permissions import IsAdminUser


class HomeView(ViewSet):
    permission_classes = [IsAdminUser]   #  只有超级管理员才能访问
    """用户总数"""
    @action(methods=['get'],detail=False)
    def total_count(self,request):

        count = User.objects.filter(is_active=True).count()
        date = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)).date()

        return Response({
            'count':count,
            'date':date
        })

    @action(methods=['get'],detail=False)
    # 日增用户统计
    def day_increment(self,request):
        # 1.获得当日日期
        date = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))
        # 2.过滤出当天新建用户数量
        count  = User.objects.filter(date_joined__gte=date.replace(hour=0,minute=0,second=0)-timedelta(hours=8,minutes=6,seconds=0)).count()
        # 3. 返回数据
        return Response({
            'count':count,
            'date':date.date()
        })

    @action(methods=['get'],detail=False)
    def day_active(self,request):
        """日活跃用户统计"""
        # 获得当日日期
        date = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))

        # 根据当日日期过滤出，当前登录用户
        sh = date.replace(hour=0,minute=0,second=0)-timedelta(hours=8,minutes=6,seconds=0)
        count = User.objects.filter(last_login__gte=sh).count()

        return Response({
            'count':count,
            'date':date.date()
        })

    @action(methods=['get'],detail=False)
    def day_orders(self,request):
        """日下单用户量统计"""
        # 1.获得当日日期
        data = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))

        # 2.过滤出当日下单用户
        sh = data.replace(hour=0,minute=0,second=0)-timedelta(hours=8,minutes=6,seconds=0)
        order_list = OrderInfo.objects.filter(create_time__gte=sh)
        # 3.从订单表中获得关联的主表数据对象
        user_list = []
        for order in order_list:
            user_list.append(order.user)
        count = len(set(user_list))

        return Response({
            'count':count,
            'data':data
        })

    @action(methods=['get'], detail=False)
    def month_increment(self,request):
        """日分类商品访问量月增用户统计"""
        # 1.获得当天日期(获得本地零时)   tzinfo=pytz.timezone(settings.TIME_ZONE)
        data = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))\
            .replace(hour=0,minute=0,second=0)
        # 起始日期
        start_data = data - timedelta(days=29)

        result_list = []
        # 循环遍历出每一天，根据每一天过滤出新增用户数量
        for index in range(30):
            calc_date = start_data + timedelta(days=index)
            # 根据calc_date日期，查询出该日期新建的用户数量
            count = User.objects.filter(date_joined__gte=data,
                                        date_joined__lt=calc_date + timedelta(days=1)
                                        ).count()

            result_list.append({
                'count':count,
                'date':calc_date.date()
            })

        return Response(result_list)

    @action(methods=['get'], detail=False)
    def goods_day_views(self,request):
        """日分类商品访问量"""
        # 过滤出当天访问数据对象
        date = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)) .replace(hour=0,minute=0,second=0)
        good_visit_queryset = GoodsVisitCount.objects.filter(create_time__gte=date)
        # 调用序列化器对数据对象序列化处理
        serializer = GoodsVisitSerializer(good_visit_queryset,many=True)
        # 返回数据
        return Response(serializer.data)









