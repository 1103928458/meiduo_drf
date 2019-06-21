from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
    # 支付界面
    url(r'^payment/(?P<order_id>\d+)/$', views.PaymentView.as_view()),
    # 支付成功回调处理
    url(r'^payment/status/$', views.PaymentStatusView.as_view()),

]
