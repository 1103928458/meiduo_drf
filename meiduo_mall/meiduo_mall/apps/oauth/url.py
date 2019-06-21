from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
    # 获取QQ登录界面url
    url(r'^qq/authorization/$', views.QQAuthURLViewe.as_view()),
    # QQ登录后的回调处理
    url(r'^oauth_callback/$', views.QQAuthView.as_view()),

    # 获取weibo登录界面url
    url(r'^weibo/authorization/$', views.SinaAuthURLView.as_view()),



]
