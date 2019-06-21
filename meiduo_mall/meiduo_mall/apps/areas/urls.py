from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
    # 获取省份
    url(r'^areas/$', views.AreasView.as_view(),name="index"),
]
