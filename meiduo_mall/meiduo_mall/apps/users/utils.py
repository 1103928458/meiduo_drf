from django.contrib.auth.backends import ModelBackend
import re
from .models import User
from itsdangerous import TimedJSONWebSignatureSerializer, BadData
from django.conf import settings


def get_user_by_account(account):
    '''根据用户名或手机号获取user'''

    try:
        if re.match(r"^1[3-9]\d{9}$",account):
            user = User.objects.get(mobile = account)

        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    return user




class UsernameMobileAuthBackend(ModelBackend):
    '''自定义认证后端'''
    def authenticate(self, request, username=None, password=None, **kwargs):

        # 1.获取user(mobile,uesrname)
        user = get_user_by_account(username)

        # 2.校验密码是否正确
        if user and user.check_password(password):

            # 3.返回user
            return user



def generate_email_verify_url(user):
    '''生成邮件激活链接'''

    Serializer = TimedJSONWebSignatureSerializer(settings.EMAIL_VERIFY_URL,3600*24)
    data = {"user_id":user.id,"email":user.email}
    token = Serializer.dumps(data).decode()
    verify_url = settings.EMAIL_VERIFY_URL + "?token" + token
    return verify_url


def check_verify_token(token):
    '''对token解密'''
    Serializer = TimedJSONWebSignatureSerializer(settings.EMAIL_VERIFY_URL, 3600 * 24)
    try:
        data = Serializer.loads(token)
    except BadData:
        return None
    else:
        user_id  = data.get("user_id")
        email = data.get("email")
        try:
            user = User.objects.get(id= user_id,email=email)
        except User.DoesNotExist:
            return None
        else:
            return user