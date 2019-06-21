import re

from django.shortcuts import render,redirect


from QQLoginTool.QQtool import OAuthQQ
from django.views import View
from django.conf import settings
from django import http

import logging

from django_redis import get_redis_connection
from carts.utils import merge_cart_cookie_to_redis
from users.models import User

logger = logging.getLogger("django")
from meiduo_mall.utils.response_code import RETCODE

from .models import OAuthQQUser
from django.contrib.auth import login
from .utils import generate_openid_signature,check_openid_signature
from .import sinaweibopy3
from .models import OAuthSinaUser



class QQAuthURLViewe(View):
    """提供QQ登录url"""

    def get(self, request):
        # 获取查询参数中的next，获取用户从哪里去到login界面
        next = request.GET.get("next") or "/"  # 既有接收也有校验，如果接收位None就跳转到根路由

        # 创建qq sdk对象
        auth_qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,  # app id
                          client_secret=settings.QQ_CLIENT_SECRET,  # app key
                          redirect_uri=settings.QQ_REDIRECT_URI,  # 登陆成功之后的回调地址
                          state=next)  # 记录界面跳转来源

        # 调用sdk中的get_qq_url方法得到拼接好的qq登录url
        login_url = auth_qq.get_qq_url()

        # 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': "ok", "login_url": login_url})


class QQAuthView(View):
    """qq登录完成的回调处理"""
    def get(self,request):
        # 1.获取查询参数中的code
        code = request.GET.get("code")

        # 2.校验
        if code is None:   # 如果code没有获取到
            return http.HttpResponseForbidden("缺少code")

        # 3.再次创建一个qq登录的SDK对象
        auth_qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,  # app id
                          client_secret=settings.QQ_CLIENT_SECRET,  # app key
                          redirect_uri=settings.QQ_REDIRECT_URI)  # 登陆成功之后的回调地址

        try:
            # 4.调用SDK中的get_access_token(code) 得到access_token
            access_token = auth_qq.get_access_token(code)
            # 5.调用SDK中的get_open_id（access_token）方法得到openid
            openid = auth_qq.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError("QQ的OAuth2.0认证失败")

        try:
            # 查询表中是否有当前这个openid
            oauth_qq = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果没有查询到openid，说明此qq是一个新的还没有绑定过美多的用户，应该去绑定
            openid = generate_openid_signature(openid)
            return render(request,"oauth_callback.html",{"open":openid})


        else:

            # 如果查询到openid，说明之前已绑定，直接登录
            user = oauth_qq.user    # 获取openid所关联的用户
            login(request,user)    # 状态保持
            next = request.GET.get("state")  # 获取用户界面来源
            response = redirect(next or "/")   #  创建响应对象及重定向

            # 向cookie中设置usernsme以备在状态栏显示登录用户的用户名
            response.set_cookie("username",user.username,max_age=settings.SESSION_COOKIE_AGE)

            # 再此做合并购物车
            merge_cart_cookie_to_redis(request, response)

            return response


    def post(self,request):
        """绑定用户处理"""
        # 1.接收表单数据
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        sms_code = request.POST.get("sms_code")
        openid = request.POST.get("openid")

        # 2.校验
        if all([mobile,password,sms_code]) is False:
            return http.HttpResponseForbidden("缺少参数")

        # 判断手机号是否正常
        if not re.match(r"^1[3-9]\d{9}$",mobile):
            return http.HttpResponseForbidden("您输入的手机号格式不正确")
        # 检查密码是否合格
        if not re.match(r"^[0-9A-Za-z]{8,20}$",password):
            return http.HttpResponseForbidden("请输入8-20位密码")
        # 检查短信验证码
        #1.连接redis数据库
        redis_conn = get_redis_connection("verify_code")
        # 获取当前数据库短信验证码
        sms_code_server = redis_conn.get("sms_%s" % mobile)
        # 从数据库取出数据位bytes类型需要解码
        sms_code_server = sms_code_server.decode()
        # 如果接收的验证码为空
        if sms_code_server is None:
            return render(request,"oauth_callback.html",{"sms_code_errmsg":"无效验证码"})

        # 如果接收验证码于当前数据库查询的验证码不一致
        if sms_code != sms_code_server:
            return render(request,"oauth_callback.html",{"sms_code_errmsg":"验证码错误"})

        # 对openid解密
        openid = check_openid_signature(openid)
        if openid is None:
            return http.HttpResponseForbidden("openid无效")

        # 先用手机号查询user表，判断当前手机号是新用户，还是已存在用户
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 说明是新用户，需要创建一个用户
            user = User.objects.create_user(mobile=mobile,password=password,username=mobile)
        else:
            # 校验这个旧用户他的密码对不对
            if user.check_password(password) is False:
                return render(request,"oauth_callback.html",{"account_errmsg":"用户名或密码错误"})

        #   绑定用户
        OAuthQQUser.objects.create(
            openid = openid,
            user =user
        )

        # 状态保持
        login(request, user)  # 状态保持
        next = request.GET.get("state")  # 获取用户界面来源
        response = redirect(next or "/")  # 创建响应对象及重定向

        # 向cookie中设置usernsme以备在状态栏显示登录用户的用户名
        response.set_cookie("username", user.username, max_age=settings.SESSION_COOKIE_AGE)

        # 再此做合并购物车
        merge_cart_cookie_to_redis(request, response)

        # 3.响应
        return response



class SinaAuthURLView(View):
    '''微博登录提供weibo登录页面网址'''

    def get(self, request):
        # 获取查询参数中的next，获取用户从哪里去到login界面
        next = request.GET.get("next") or "/"  # 既有接收也有校验，如果接收位None就跳转到根路由

        # 创建weibo sdk对象

        # self.client_id = app_key
        # self.client_secret = app_secret
        # # self.redirect_uri = redirect_uri

        auth_weibo = sinaweibopy3.APIClient(app_key=settings.APP_KEY,
                                            app_secret=settings.APP_SECRET,
                                            redirect_uri=settings.WEIBO_REDIRECT_URI)

        # 调用sdk中的get_authorize_url方法得到拼接好的weibo登录url
        login_url = auth_weibo.get_authorize_url()

        # 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': "ok", "login_url": login_url})



class WeiboAuthView(View):
    """微博登录完成的回调处理"""

    def get(self, request):
        # 1.获取查询参数中的code
        code = request.GET.get("code")

        # 2.校验
        if code is None:  # 如果code没有获取到
            return http.HttpResponseForbidden("缺少code")

        auth_weibo = sinaweibopy3.APIClient(app_key=settings.APP_KEY, app_secret=settings.APP_SECRET,
                               redirect_uri=settings.WEIBO_REDIRECT_URI )
        try:
            # 4.调用SDK中的get_access_token(code) 得到access_token
            result = auth_weibo.request_access_token(code)
            access_token = result.access_token
            uid = result.uid
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError("认证失败")

        try:
            # 查询表中是否有当前这个access_token
            oauth_model = OAuthSinaUser.objects.get(access_token = access_token)
        except OAuthSinaUser.DoesNotExist:
            # 如果没有查询到access_token，说明此weibo是一个新的还没有绑定过美多的用户，应该去绑定
            access_token = generate_openid_signature(access_token)
            return render(request, "sina_callback.html", {'access_token':access_token})


        else:

            # 如果查询到openid，说明之前已绑定，直接登录
            user = oauth_model.user  # 获取openid所关联的用户
            login(request, user)  # 状态保持
            next = request.GET.get("state")  # 获取用户界面来源
            response = redirect(next or "/")  # 创建响应对象及重定向

            # 向cookie中设置usernsme以备在状态栏显示登录用户的用户名
            response.set_cookie("username", user.username, max_age=settings.SESSION_COOKIE_AGE)

            # 再此做合并购物车
            merge_cart_cookie_to_redis(request, response)

            return response
