from django.http import HttpResponseForbidden
from django import http
from django.shortcuts import render, redirect
import re, json
from django.contrib.auth import login, authenticate, logout, mixins
from .models import User, Address
from meiduo_mall.utils.response_code import RETCODE
from django_redis import get_redis_connection
from random import randint

from django.views import View
from celery_tasks.email.tasks import send_verify_email
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .utils import generate_email_verify_url, check_verify_token
import logging
from goods.models import SKU
from carts.utils import merge_cart_cookie_to_redis
from .utils import get_user_by_account
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from celery_tasks.sms.tasks import send_sms_code

Logger = logging.getLogger("django")


class RegisterView(View):

    def get(self, request):
        """提供注册页面"""
        return render(request, "register.html")

    def post(self, request):
        """注册公功能逻辑"""
        # 1.接收前端传入的表单数据
        # 用户名，密码，手机号，短信验证码，同意协议
        query_dict = request.POST
        username = query_dict.get("username")
        password = query_dict.get("password")
        password2 = query_dict.get("password2")
        mobile = query_dict.get("mobile")
        sms_code = query_dict.get("sms_code")
        allow = query_dict.get("allow")  # 单选框，如果勾选传入的就是“on”，如果没有勾选传入的是None
        # 2.检验数据是否满足需求
        if all([username, password, password2, mobile, sms_code, allow]) is False:
            return http.HttpResponseForbidden("缺少必要参数")

        if not re.match(r"^[a-zA-Z0-9_-]{8,20}$", password):
            return http.HttpResponseForbidden('请输入8-20位的密码')

        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')

        if not re.match(r"^1[3-9]\d{9}$", mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')

        #  短信验证码后期在补充校验逻辑
        redis_conn = get_redis_connection("verify_code")
        sms_code_server = redis_conn.get('sms_%s' % mobile)

        # 删除redis中的短信验证码，让验证码只能用一次
        redis_conn.delete('sms_%s', mobile)

        # 检验短信验证码是否过期
        if sms_code_server is None:
            return http.HttpResponseForbidden("短信验证码过期")
        sms_code_server = sms_code_server.decode()

        if sms_code != sms_code_server:
            return http.HttpResponseForbidden('请输入正确的验证码')

        # 保存数据，创建用户user
        user = User.objects.create_user(username=username, password=password, mobile=mobile)

        # 当用户登录后，将用户的user.id值存储到session  生成session  cookie
        # 记录用户的登陆状态
        login(request, user)
        # request.session["_auth_user_id"] = user.id
        # 响应：重定向到首页
        return redirect('/')


class UsernameCountView(View):
    '''判断用户名是否重复注册'''

    def get(self, request, username):
        # 从数据库查询
        count = User.objects.filter(username=username).count()
        response_data = {"count": count, "code": RETCODE.OK, "errmsg": "ok"}
        return http.JsonResponse(response_data)


class MobileCountView(View):
    '''判断手机号是否重复注册'''

    def get(self, request, mobile):
        # 从数据库查询
        count = User.objects.filter(mobile=mobile).count()
        response_data = {"count": count, "code": RETCODE.OK, "errmsg": "ok"}
        return http.JsonResponse(response_data)


class LoginView(View):
    '''用户登录'''

    def get(self, request):
        '''展示登录界面'''
        return render(request, 'login.html')

    def post(self, request):
        """用户登录逻辑"""
        # 1.接收表单数据
        username = request.POST.get("username")
        password = request.POST.get("password")
        remembered = request.POST.get("remembered")  # 是否记录密码 勾选on 不勾None

        # 2.校验
        # try:
        #     user = User.objects.get(username=username,password=password)
        # except User.DoesNotExist:
        #     return
        #
        # if user.check_password(password) is False:
        #     return

        # 修改配置文件---使用手机号码登录（多账号登录）
        # if re.match(r"^1[3-9]\d{9}$", username):
        #
        #     User.USERNAME_FIELD = "mobile"     # 使用模型类    模型类的属性：USERNAME_FIELD

        # 用户认证（django自带校验）
        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, "login.html", {"account_errmsg": "用户名或密码错误"})

        # 3.状态保持
        login(request, user)
        # 如果用户没有点击记住密码
        if remembered != "on":
            # 此行代码实际最终讲cookie中的session设置位浏览器关闭就失效
            request.session.set_expiry(0)

        next = request.GET.get("next")  # 尝试性去获取来源查询参数

        response = redirect(next or "/")

        response.set_cookie("username", user.username, max_age=3600 * 24 * 14 if remembered else None)

        # 再此做合并购物车
        merge_cart_cookie_to_redis(request, response)

        # 4.重定向首页
        return response


class LogoutView(View):
    """退出登录"""

    def get(self, request):
        # 1.清除状态保持信息
        logout(request)
        # 2.重定向到登录页面
        response = redirect("/login/")
        # 3.清除cookie中的username
        response.delete_cookie("username")
        # 4.响应
        return response


# 展示用户中心第一种方法：
# class UserInfoView(View):
#     """展示用户中心"""
#     def get(self,request):
#         """展示用户中心界面"""
#         user = request.user
#
#         # 如果用户登录就展示用户中心
#         if user.is_authenticated:   # 判断用户是否登录
#             return render(request,"user_center_info.html")
#
#         # 如果没有登录就展示登录页面
#         else:
#             return redirect("/login/?next=/info/")


# 展示用户中心第二种方法：

# class UserInfoView(View):
#     """展示用户中心"""
#     @method_decorator(login_required)   # 判断用户有没有登录
#     def get(self,request):
#         """展示用户中心界面"""
#
#         return render(request,"user_center_info.html")


# 展示用户中心第二种方法：
# mixins.LoginRequiredMixin  判断用户是否登录
class UserInfoView(mixins.LoginRequiredMixin, View):
    """展示用户中心"""

    def get(self, request):
        """展示用户中心界面"""

        return render(request, "user_center_info.html")


class EmailView(mixins.LoginRequiredMixin, View):
    '''设置邮箱'''

    def put(self, request):
        # 1.接收数据
        json_dict = json.loads(request.body.decode())
        email = json_dict.get("email")

        # 2.校验
        if not email:
            return http.HttpResponseForbidden('缺少email参数')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email有误')

        # 3.修改用户的email字段
        user = request.user
        # user.email = email
        # user.save()
        User.objects.filter(username=user.username, email="").update(email=email)

        # 再次给用户发一封激活邮件

        verify_url = generate_email_verify_url(user)  # 生成激活邮箱url
        send_verify_email.delay(email, verify_url)  # 使用异步任务

        # 4.响应
        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "添加邮箱成功"})


class VerifyEmailView(View):
    '''激活邮箱'''

    def get(self, request):
        # 接收参数中的token
        token = request.GET.get("token")
        # 校验
        if token is None:
            return http.HttpResponseForbidden("缺少token")
        # 对token解密并获取user
        user = check_verify_token(token)

        if user is None:
            return http.HttpResponseForbidden("token无效")
        # 修改指定user的email_active字段
        user.email_active = True
        user.save()
        # 响应
        # 激活成功回到用户中心
        return redirect("/info/")


class AddressView(mixins.LoginRequiredMixin, View):
    '''展示用户收货地址'''

    def get(self, request):
        """用户收货地址展示"""
        # 查询当前用户的所有收货地址
        user = request.user
        addresses_qs = Address.objects.filter(user=user, is_deleted=False)
        # 定义一个列表变量用来包装所有的收货地址字典数据
        addresses = []
        for address_model in addresses_qs:
            addresses.append({
                "id": address_model.id,
                "title": address_model.title,
                "receiver": address_model.receiver,
                "province": address_model.province.name,
                "province_id": address_model.province.id,
                "city": address_model.city.name,
                "city_id": address_model.city.id,
                "district": address_model.district.name,
                "district_id": address_model.district.id,
                "place": address_model.place,
                "mobile": address_model.mobile,
                "tel": address_model.tel,
                "email": address_model.email
            })
        # 准备渲染数据
        context = {
            "addresses": addresses,
            "default_address_id": user.default_address_id
        }
        return render(request, "user_center_site.html", context)


class CreateAddressView(mixins.LoginRequiredMixin, View):
    def post(self, request):
        # 判断用户的收货地址是否上限
        user = request.user
        count = user.addresses.filter(is_deleted=False).count()
        if count >= 20:
            return http.JsonResponse({"code": RETCODE.THROTTLINGERR, "errmsg": "地址已达到上限"})
        # 接收请求体数据
        json_dict = json.loads(request.body.decode())
        title = json_dict.get("title")
        receiver = json_dict.get("receiver")
        province_id = json_dict.get("province_id")
        city_id = json_dict.get("city_id")
        district_id = json_dict.get("district_id")
        place = json_dict.get("place")
        mobile = json_dict.get("mobile")
        tel = json_dict.get("tel")
        email = json_dict.get("email")
        # 校验
        if all([title, receiver, province_id, city_id, district_id, place, mobile]) is False:
            return http.HttpResponseForbidden("缺少必传参数")

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')
        try:
            # 保存收货地址数据
            address_model = Address.objects.create(
                user=request.user,

                title=title,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email,
            )
        except Exception as e:
            Logger.error(e)
            return http.HttpResponseForbidden({"code": RETCODE.PARAMERR, "errmsg": "新增收货地址失败"})

        # 如果当前用户还没有默认收货地址，就把当前新增的这个地址设置为他的默认地址
        if user.default_address is None:
            user.default_address = address_model
            user.save()

        # 把保存好的模型对象转换成字典，再响应给前端
        address_dict = {
            "id": address_model.id,
            "title": address_model.title,
            "receiver": address_model.receiver,
            "province": address_model.province.name,
            "province_id": address_model.province.id,
            "city": address_model.city.name,
            "city_id": address_model.city.id,
            "district": address_model.district.name,
            "district_id": address_model.district.id,
            "place": address_model.place,
            "mobile": address_model.mobile,
            "tel": address_model.tel,
            "email": address_model.email
        }
        # 响应
        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "新增地址成功", "address": address_dict})


class UpdateDestroyAddressView(mixins.LoginRequiredMixin, View):
    """修改和删除用户地址操作"""

    def put(self, request, address_id):

        # 接收请求体数据
        json_dict = json.loads(request.body.decode())
        title = json_dict.get("title")
        receiver = json_dict.get("receiver")
        province_id = json_dict.get("province_id")
        city_id = json_dict.get("city_id")
        district_id = json_dict.get("district_id")
        place = json_dict.get("place")
        mobile = json_dict.get("mobile")
        tel = json_dict.get("tel")
        email = json_dict.get("email")
        # 校验
        if all([title, receiver, province_id, city_id, district_id, place, mobile]) is False:
            return http.HttpResponseForbidden("缺少必传参数")

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        try:
            # 修改收货地址数据
            Address.objects.filter(id=address_id).update(

                title=title,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email,
            )
        except Exception as e:
            Logger.error(e)
            return http.HttpResponseForbidden({"code": RETCODE.PARAMERR, "errmsg": "修改收货地址失败"})

        # 获取到修改后的地址模型对象
        address_model = Address.objects.get(id=address_id)
        address_dict = {
            "id": address_model.id,
            "title": address_model.title,
            "receiver": address_model.receiver,
            "province": address_model.province.name,
            "province_id": address_model.province.id,
            "city": address_model.city.name,
            "city_id": address_model.city.id,
            "district": address_model.district.name,
            "district_id": address_model.district.id,
            "place": address_model.place,
            "mobile": address_model.mobile,
            "tel": address_model.tel,
            "email": address_model.email
        }
        # 响应
        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "修改地址成功", "address": address_dict})

    def delete(self, request, address_id):
        """删除地址"""
        try:
            address = Address.objects.get(id=address_id)
            address.is_deleted = True
            address.save()
            return http.JsonResponse({"code": RETCODE.OK, "errmsg": "删除地址成功"})
        except Address.DoesNotExist:
            return http.JsonResponse({"code": RETCODE.PARAMERR, "errmsg": "address_id不存在"})


class DefaultAddressView(mixins.LoginRequiredMixin, View):
    """设置默认地址"""

    def put(self, request, address_id):
        # 查询指定id的收货地址
        try:
            address = Address.objects.get(id=address_id)
            user = request.user
            # 把指定的收货地址设置给user的default_address字段
            user.default_address = address
            user.save()
            # 响应
            return http.JsonResponse({"code": RETCODE.OK, "errmsg": "设置默认地址成功"})

        except Address.DoesNotExist:
            return http.JsonResponse({"code": RETCODE.PARAMERR, "errmsg": "设置默认地址失败"})


class UpdateTitleAddressView(mixins.LoginRequiredMixin, View):
    """修改用户收货地址标题"""

    def put(self, request, address_id):
        # 接收请求体中的地址标题
        json_dict = json.loads(request.body.decode())
        title = json_dict.get("title")

        # 校验
        if title is None:
            return http.JsonResponse({"code": RETCODE.PARAMERR, "errmsg": "缺少必传参数"})

        # 把要修改的收货地址获取
        try:
            address = Address.objects.get(id=address_id)

            # 修改address的title
            address.title = title
            address.save()

            # 响应
            return http.JsonResponse({"code": RETCODE.OK, "errmsg": "修改地址标题成功"})
        except Address.DoesNotExist:
            return http.JsonResponse({"code": RETCODE.PARAMERR, "errmsg": "修改地址标题失败"})


class CheckPaswordView(mixins.LoginRequiredMixin, View):
    """修改用户密码"""

    def get(self, request):
        return render(request, "user_center_pass.html")

    def post(self, request):
        # 接收请求体中的表单数据
        qury_dict = request.POST
        old_password = qury_dict.get("old_pwd")
        new_password = qury_dict.get("new_pwd")
        new_password2 = qury_dict.get("new_cpwd")

        # 校验
        if all([old_password, new_password, new_password2]) is False:
            return http.HttpResponseForbidden("缺少必传参数")

        user = request.user
        if user.check_password(old_password) is False:
            return render(request, "user_center_pass.html", {"origin_pwd_errmsg": "原密码错误"})

        # 检验密码
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return http.HttpResponseForbidden('密码最少8位，最长20位')
        if new_password != new_password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')

        # 修改用户密码 set_password方法
        user.set_password(new_password)
        user.save()
        # 清除状态保持信息
        logout(request)

        # 清除cookie中的username
        response = redirect("/login")
        response.delete_cookie("username")

        # 重定向到登录界面
        return response


class UserBrowseHistory(mixins.LoginRequiredMixin, View):
    """商品浏览记录"""

    def post(self, request):
        # 接收请求体中的sku_id
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get("sku_id")

        try:
            # 校验sku_id的真实性
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('sku不存在')
        # 创建redis链接
        redis_conn = get_redis_connection("history")

        pl = redis_conn.pipeline()

        # 获取当前用户
        user = request.user

        # 拼接list的key
        key = 'history_%s' % user.id
        # 先去重
        pl.lrem(key, 0, sku_id)

        # 添加到列表的开头
        pl.lpush(key, sku_id)

        # 截取列表前五位
        pl.ltrim(key, 0, 4)
        # 执行
        pl.execute()
        # 响应
        return http.JsonResponse({"code": RETCODE, "errmsg": "ok"})

    def get(self, request):
        """获取用户浏览记录逻辑"""

        # 1.获取当前的登录用户对象
        user = request.user
        # 2.创建redis链接对象
        redis_conn = get_redis_connection("history")
        # 3.获取当前用户在redis中所有的浏览记录列表
        sku_ids = redis_conn.lrange("history_%s" % user.id, 0, -1)

        skus = []  # 用来保存sku字典
        # 4.在通过列表中的sku_id获取到每个sku模型
        for sku_id in sku_ids:
            # 5.再将sku模型转换成字典
            sku_model = SKU.objects.get(id=sku_id)
            skus.append({
                "id": sku_model.id,
                "name": sku_model.name,
                "default_image_url": sku_model.default_image.url,
                "price": sku_model.price
            })
        # 6.响应
        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "ok", "skus": skus})


class ForgetPassword(View):
    """忘记密码"""

    def get(self, request):
        return render(request, 'find_password.html')


class GetMobileAndCode(View):
    """修改密码"""

    def get(self, request, username):

        image_code = request.GET.get('text')
        uuid = request.GET.get('image_code_id')

        if all([username, image_code, uuid]) is False:
            return http.HttpResponseForbidden("缺少必要参数")

        user = get_user_by_account(username)

        if user is None:
            return http.HttpResponseForbidden('用户名不存在')

        else:
            mobile = user.mobile

        # 创建redis数据库链接
        redis_conn = get_redis_connection('verify_code')

        # 获取redis数据库中取出图形验证码
        redis_image_code = redis_conn.get("img_%s" % uuid)

        redis_conn.delete("img_%s" % uuid)

        if redis_image_code is None or image_code.lower() != redis_image_code.decode().lower():
            return http.JsonResponse({'code': 'ok', 'errmsg': "验证码错误"}, status=400)

        # 对数据加密
        data = {'mobile': mobile}
        serializer = Serializer(settings.SECRET_KEY, 60)

        access_token = serializer.dumps(data).decode()

        return http.JsonResponse({"mobile": mobile, "access_token": access_token})


class Send_sms_code(View):
    """发送短信验证码"""

    def get(self, request):
        access_token = request.GET.get('access_token')

        if access_token is None:
            return http.HttpResponseForbidden('access_token为空')

        serializer = Serializer(settings.SECRET_KEY, 60)

        try:
            data = serializer.loads(access_token)
            mobile = data.get('mobile')

        except BadData:
            return http.HttpResponseForbidden('数据有误')

        redis_conn = get_redis_connection('verify_code')
        send_flag = redis_conn.get('send_flag_%s' % mobile)

        if send_flag:  # 判断有无标记
            return http.JsonResponse({'errmsg': '频繁发送短信'})

        sms_code = "%06d" % randint(0, 999999)

        print(sms_code)

        # 5.把短信验证码存储到redis，以备后期注册时校验
        redis_conn.setex('sms_%s' % mobile, 300, sms_code)
        # 5.1向redis存储一个此手机号以发送过短信的标记
        redis_conn.setex('send_flag_%s' % mobile, 60, 1)

        send_sms_code.delay(mobile, sms_code)
        return http.JsonResponse({'message': 'ok'})


class Check_sms_code(View):
    """验证手机号"""

    def get(self, request, username):
        sms_code = request.GET.get('sms_code')

        if all([username, sms_code]) is False:
            return http.HttpResponseForbidden("缺少必传参数")

        # 自定义认证后端
        username = get_user_by_account(username)

        if username is None:
            return http.HttpResponseForbidden('用户名不存在')

        else:
            user_id = username.id
            mobile = username.mobile

        # 连接redis数据库
        redis_conn = get_redis_connection('verify_code')
        redis_conn_code = redis_conn.get('sms_%s' % mobile)

        if sms_code != redis_conn_code.decode():
            return http.HttpResponseForbidden('验证码错误')

        data = {'mobile': mobile}

        serializer = Serializer(settings.SECRET_KEY, 300)
        access_token = serializer.dumps(data).decode()
        return http.JsonResponse({
            'user_id': user_id,
            'access_token': access_token
        })


class Check_pwd(View):
    """检查密码---重置密码"""

    def post(self, request, user_id):
        json_dict = json.loads(request.body.decode())
        password = json_dict.get('password')
        password2 = json_dict.get('password2')
        access_token = json_dict.get('access_token')

        if all(([password, password2, access_token])) is None:
            return http.HttpResponseForbidden("缺少必传参数")

        if password != password2:
            return http.HttpResponseForbidden('密码不一致')

        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('密码最少8位，最长20位')

        user = User.objects.get(id=user_id)
        mobile = user.mobile

        serializer = Serializer(settings.SECRET_KEY, 300)
        data = serializer.loads(access_token)
        mobile_data = data.get('mobile')

        if mobile != mobile_data:
            return http.HttpResponseForbidden('数据错误')

        user.set_password(password)
        user.save()

        return http.JsonResponse({'code': '修改密码成功'})
