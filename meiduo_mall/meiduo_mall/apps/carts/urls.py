from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
    # 购物车操作
    url(r'^carts/$', views.CartsView.as_view()),
    # 购物车全选
    url(r'^carts/$', views.CartsSelectedAllView.as_view()),
    # 商品页面右上角简单购物车
    url(r'^carts/simple/$', views.CartsSimpleView.as_view()),

]
