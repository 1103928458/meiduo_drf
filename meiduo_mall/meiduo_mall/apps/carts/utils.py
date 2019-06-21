import pickle,base64
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request,response):
    # 获取除cookie购物车数据
    cart_str = request.COOKIES.get("cart")

    # 获取用户对象(必须在执行完login之后再去拿user不然是匿名用户)
    user = request.user
    # 判断有没有cookie购物车数据
    if cart_str is None:
        # 如果购物车没有数据就直接返回
        return
    # 将cookie_str转换成dict
    cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))

    # 创建redis链接对象
    redis_conn = get_redis_connection("carts")

    # 遍历cookie大字典
    # {sku_id_1:{'count':1,'selected':Ture}}

    for sku_id,sku_dict in cart_dict.items():
        redis_conn.hset('cart_%s'% user.id,sku_id,sku_dict['count'])

        # sadd或srem来操作勾选状态
        if sku_dict['selected']:
            redis_conn.sadd('selected_%s'%user.id,sku_id)
        else:
            redis_conn.srem('selected_%s'%user.id,sku_id)


    # 删除cookie购物车数据
    response.delete_cookie('carts')




