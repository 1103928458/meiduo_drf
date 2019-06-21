from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
    # 注册界面
    url(r'^register/$', views.RegisterView.as_view(),name="register"),
    # 判断用户名是否重复注册
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    # 判断手机号是否注册
    url(r'^mobile/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    # 用户登录
    url(r'^login/$', views.LoginView.as_view()),
    # 退出登录
    url(r'^logout/$', views.LogoutView.as_view()),
    # 用户中心
    url(r'^info/$', views.UserInfoView.as_view(),name="info"),
    # 添加邮箱
    url(r'^emails/$', views.EmailView.as_view()),
    # 激活邮箱
    url(r'^emails/verification$', views.VerifyEmailView.as_view()),
    # 展示收货地址
    url(r'^addresses/$', views.AddressView.as_view(),name="address"),
    # 新增地址
    url(r'^addresses/create/$', views.CreateAddressView.as_view()),
    # 用户地址修改和删除
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),
    # 用户设置默认地址
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view()),
    # 修改用户地址标题
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view()),
    # 修改用户密码
    url(r'^password/$', views.CheckPaswordView.as_view()),
    # 商品浏览记录
    url(r'^browse_histories/$', views.UserBrowseHistory.as_view()),
    # 忘记密码
    url(r'^find_password/$', views.ForgetPassword.as_view()),
    # 修改密码
    url(r'^accounts/(?P<username>[a-zA-Z0-9_-]{5,20})/sms/token/', views.GetMobileAndCode.as_view()),

    # 发送验证码
    url(r'^sms_codes/', views.Send_sms_code.as_view()),

    url(r'^accounts/(?P<username>[a-zA-Z0-9_-]{5,20})', views.Check_sms_code.as_view()),
    # 重置密码
    url(r'^users/(?P<user_id>\d+)/password/$', views.Check_pwd.as_view())






]
