from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
    # 订单结算
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view()),

    # 提交订单
    url(r'^orders/commit/$', views.OrderCommitView.as_view()),

    # 提交订单成功返回界面
    url(r'^orders/success/$', views.OrderSuccessView.as_view()),
    # 全部订单
    url(r'^orders/info/1/$', views.AllOrder.as_view()),



]
