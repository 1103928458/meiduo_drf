
from django.conf.urls import url, include
from .views.user_login_views import *
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.utils import jwt_response_payload_handler
from .views.home_views import HomeView
from rest_framework.routers import SimpleRouter


urlpatterns = [
    # url(r'^authorizations/$', UserLoginView.as_view())

    # obtain_jwt_token给我们返回给前端的数据只有token，没有额外的数据
    url(r'^authorizations/$', obtain_jwt_token),
    #
    # url(r'^statistical/total_count/$', HomeView.as_view({'get':'total_count'}))


]
# 路径映射
router = SimpleRouter()
router.register(prefix='statistical',viewset=HomeView,base_name='home')
urlpatterns += router.urls