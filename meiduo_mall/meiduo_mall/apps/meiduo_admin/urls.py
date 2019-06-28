
from django.conf.urls import url, include
from .views.user_login_views import *
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.utils import jwt_response_payload_handler
from .views.home_views import HomeView
from rest_framework.routers import SimpleRouter
from meiduo_admin.views.user_views import *
from meiduo_admin.views.sku_views import *
from meiduo_admin.views.spu_views import *
from meiduo_admin.views.spec_views import *
from meiduo_admin.views.option_views import *
from meiduo_admin.views.channel_views import *
from meiduo_admin.views.brand_views import *
from meiduo_admin.views.skuimage_views import *
from meiduo_admin.views.order_views import *
from meiduo_admin.views.perms_viewset import *
from meiduo_admin.views.group_views import *
from meiduo_admin.views.admin_views import *
urlpatterns = [
    # url(r'^authorizations/$', UserLoginView.as_view())

    # obtain_jwt_token给我们返回给前端的数据只有token，没有额外的数据
    url(r'^authorizations/$', obtain_jwt_token),

    url(r'^users/$', UserView.as_view()),

    url(r'^skus/$', SKUViews.as_view({'get':'list','post':'create'})),
    url(r'^skus/(?P<pk>\d+)/$', SKUViews.as_view({'delete':'destroy','get':'retrieve','put':'update'})),
    url(r'^skus/categories/$', GoodsCategoryViews.as_view()),
    url(r'^goods/simple/$', SpuViews.as_view()),

    url(r'^goods/(?P<pk>\d+)/specs/$', SpecOptView.as_view()),
    # spu商品所有数据,新建单一资源
    url(r'^goods/$',SpuView.as_view({'get':'list','post':'create'})),

    url(r'^goods/(?P<pk>\d+)/$',SpuView.as_view({'delete':'destroy','put':'update','get':'retrieve'})),

    url(r'^goods/brands/simple/$', BrandViews.as_view()),

    url(r'^goods/channel/categories/$', GoodsCategoryView.as_view()),

    url(r'^goods/channel/categories/(?P<pk>\d+)/$', GoodsCategoryView.as_view()),

    url(r'^goods/specs/$', SpecModelView.as_view({'get':'list','post':'create'})),
    url(r'^goods/specs/(?P<pk>\d+)/$', SpecModelView.as_view({'get':'retrieve','put':'update','delete':'destroy'})),

# specs/options/
    url(r'^specs/options/$', OptionViews.as_view({'get':'list','post':'create'})),
    url(r'^specs/options/(?P<pk>\d+)/$', OptionViews.as_view({'put':'update','delete':'destroy'})),
    url(r'^goods/specs/simple/$', SpecSimpleView.as_view()),
    # 获得频道所有数据
    url(r'^goods/channels/$',ChannelViewSet.as_view({'get':'list','post':'create'})),
    url(r'^goods/channels/(?P<pk>\d+)/$',ChannelViewSet.as_view({'get':'retrieve','put':'update','delete':'destroy'})),
    url(r'^goods/channel_types/$',GoodsChannelGroupViewset.as_view({'get':'list'})),
    url(r'^goods/categories/$',GoodsCategoryViewset.as_view({'get':'list'})),

    # 品牌管理
    url(r'^goods/brands/$',BrandSViewset.as_view({'get':'list','post':'create'})),
    url(r'^goods/brands/(?P<pk>\d+)/$',BrandSViewset.as_view({'get':'retrieve','put':'update','delete':'destroy'})),

    # 图片管理
    url(r'^skus/images/$',SkuimageViewset.as_view({'get':'list','post':'create'})),
    url(r'^skus/images/(?P<pk>\d+)/$',SkuimageViewset.as_view({'put':'update','delete':"destroy"})),

    url(r'^skus/simple/$',SKUViewset.as_view({'get':'list'})),
    url(r'^skus/simple/(?P<pk>\d+)/$',SKUViewset.as_view({'get':'list'})),

    # 订单管理
    url(r'^orders/$',OrederViewset.as_view({'get':'list'})),
    url(r'^orders/(?P<pk>\d+)/$',OrederViewset.as_view({'get':'retrieve'})),

    url(r'^orders/(?P<pk>\d+)/status/$',OrederViewset.as_view({'put':'update'})),

    # 权限管理
    url(r'^permission/perms/$',PermViewSet.as_view({'get':'list','post':'create'})),
    # 编辑
    url(r'^permission/perms/(?P<pk>\d+)/$',PermViewSet.as_view({'get':'retrieve','put':'update','delete':"destroy"})),
    # 获得新建权限可选数据
    url(r'^permission/content_types/$',PermViewSet.as_view({'get':'content_types'})),
    # 用户组管理
    url(r'^permission/groups/$',GroupViewset.as_view({'get':'list','post':'create'})),
    url(r'^permission/groups/(?P<pk>\d+)/$',GroupViewset.as_view({'get':'retrieve','put':'update','delete':"destroy"})),

    url(r'^permission/simple/$',GroupViewset.as_view({'get':'permission_simple'})),
    # 管理员操作
    url(r'^permission/admins/$',AdminViewset.as_view({'get':'list','post':'create'})),
    url(r'^permission/admins/(?P<pk>\d+)/$',AdminViewset.as_view({'get':'retrieve','put':'update','delete':"destroy"})),
    # 获得管理员可选分组
    url(r'^permission/groups/simple/$',AdminViewset.as_view({'get':'simple'})),

# permission/groups/simple/





]
# 路径映射
router = SimpleRouter()
router.register(prefix='statistical',viewset=HomeView,base_name='home')
urlpatterns += router.urls