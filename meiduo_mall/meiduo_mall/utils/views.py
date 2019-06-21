from django.contrib.auth import mixins
from django.views import View

# 判断用户登录----用于继承
class LoginRequiredView(mixins.LoginRequiredMixin,View):
    pass