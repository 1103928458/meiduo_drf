from django.views import View
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django import http
from meiduo_mall.utils.response_code import RETCODE
from random import randint
# from celery_tasks.sms.yuntongxun import CCP
import logging
from meiduo_mall.apps.verifications.constans import SMS_CODE_EXPIRES
from celery_tasks.sms.tasks import send_sms_code
logger = logging.getLogger("django")
# Create your views here.
class ImageCodeView(View):
    '''图形验证码'''

    def get(self, request, uuid):
        # 1.调用SDK方法，生产图像验证码
        # name:表示sdk内部生成的唯一表示
        # text：表示图形验证码文本内容
        # image：图片bytes类型数据
        name, text, image = captcha.generate_captcha()
        # 2.将图形验证码的文字存储到redis
        redis_conn = get_redis_connection("verify_code")
        redis_conn.setex("img_%s" % uuid,SMS_CODE_EXPIRES, text)
        # 3.响应数据给前端
        return http.HttpResponse(image, content_type="image/png")


class SMSCodeView(View):
    '''短信验证码'''

    def get(self, request, mobile):
        # 连接数redis据库
        redis_conn = get_redis_connection("verify_code")
        # 0.尝试的去redis中获取此手机号有没有发送过短信的标记，如果有，直接响应
        send_flag = redis_conn.get('send_flag_%s'%mobile)

        if send_flag:    # 判断有无标记
            return http.JsonResponse({'code':RETCODE.THROTTLINGERR,'errmsg':'频繁发送短信'})

        """

        :param request: 请求对象
        :param mobile: 手机号
        :return: 返回json格式
        """
        # 接收参数
        # 1.提取前端url查询参数传入的image_code,uuid
        image_code_client = request.GET.get("image_code")
        uuid = request.GET.get("uuid")


        # 2.校验 all（）
        if all([image_code_client, uuid]) is False:
            return http.HttpResponseForbidden("缺少必要参数")

        # 从数据库取出的图形验证码
        image_code_server = redis_conn.get("img_%s" % uuid)

        # 删除redis中的图形验证码，让验证码只能用一次
        redis_conn.delete('img_%s', uuid)

        # 判断redis中存储的图像验证码是否已过期
        if image_code_server is None:
            return http.JsonResponse({"code": RETCODE.IMAGECODEERR, "errmsg": "图形验证码已失效"})

        # 从redis中取出来的数据都是bytes类型
        image_code_server = image_code_server.decode()
        # 3.获取redis中的图形验证码和前端传入的进行比较
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({"code": RETCODE.IMAGECODEERR, "errmsg": "请输入正确的验证码"})
        # 4.生成一个随机的6位数字，作为短信验证码
        sms_code = "%06d" % randint(0, 999999)
        # 输出验证码日志
        logger.info(sms_code)

        # 管道技术
        pl = redis_conn.pipeline()

        # 5.把短信验证码存储到redis，以备后期注册时校验
        pl.setex('sms_%s' % mobile,SMS_CODE_EXPIRES, sms_code)
        # 5.1向redis存储一个此手机号以发送过短信的标记
        pl.setex('send_flag_%s'%mobile,60,1)

        # 执行管道
        pl.execute()

        # 6.发短信 容联云通讯
        # CCP().send_template_sms(mobile,[sms_code,5],1)
        send_sms_code.delay(mobile,sms_code)   # 把任务外包给celery
        # 7.响应
        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "发送验证码成功"})
