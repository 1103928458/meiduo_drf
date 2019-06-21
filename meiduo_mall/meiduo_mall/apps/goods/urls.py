from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
    # 商品列表界面
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view()),
    # 商品热销排行
    url(r'^hot/(?P<category_id>\d+)/$', views.HotGoodView.as_view()),
    # 商品详情
    url(r'^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view()),
    # 商品访问量
    url(r'^visit/(?P<category_id>\d+)/$', views.DetailVisitView.as_view()),
]
