from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django_redis import get_redis_connection
from decimal import Decimal
import json
from django import http
from django.utils import timezone
from django.db import transaction    #  开启事物


from users.models import Address
from goods.models import SKU
from .models import OrderInfo,OrderGoods
from meiduo_mall.utils.response_code import RETCODE

class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""

    def get(self, request):
        # 查询数据
        addresses = Address.objects.filter(user=request.user, is_deleted=False)

        # 判断查集有没有值
        addresses = addresses if addresses.exists() else None

        user = request.user
        # 链接redis数据库
        redis_conn = get_redis_connection('carts')
        # 获取出hash和set集合中购物车数据
        redis_dict = redis_conn.hgetall('carts_%s' % user.id)
        selected_ids = redis_conn.smembers('selected_%s' % user.id)
        # 准备一个字典变量用来保存勾选的商品id和count
        cart_dict = {}
        for sku_id_bytes in selected_ids:
            cart_dict[int(sku_id_bytes)] = int(redis_dict[sku_id_bytes])

        # 获取勾选商品的sku模型
        skus = SKU.objects.filter(id__in=cart_dict.keys())

        total_count = 0  # 统计商品数量
        total_amount = Decimal('0.00')  # 商品总价
        for sku in skus:
            # 给sku模型多定义count属性记录数量
            sku.count = cart_dict[sku.id]
            sku.amount = sku.price * sku.count  # 小计

            # 累加商品总量
            total_count += sku.count
            # 累加商品总价
            total_amount += sku.amount

        # 运费
        freight = Decimal('10.00')

        # 构造模板渲染的数据
        # 响应
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight
        }
        return render(request, 'place_order.html', context)


class OrderCommitView(LoginRequiredMixin, View):
    """提交订单逻辑"""

    def post(self, request):

        # 1.保存一个订单基本信息记录
        # 获取请求体数据
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get("address_id")
        pay_method = json_dict.get("pay_method")

        # 校验
        if all([address_id, pay_method]) is False:
            return http.HttpResponseForbidden("缺少必传参数")
        try:
            address = Address.objects.get(id=address_id)

        except Address.DoesNotExist:
            return http.HttpResponseForbidden("地址不存在")

        # PAY_METHODS_ENUM = {
        #     "CASH": 1,
        #     "ALIPAY": 2

        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'],
                              OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden("支付方式不存在")

        # 生成订单编号：获取当前时间 + 用户id
        user = request.user
        order_id = timezone.now().strftime("%Y%m%d%H%M%S") + ("%09d" % user.id)

        status = OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else OrderInfo.ORDER_STATUS_ENUM['UNSEND']

        # 手动开启事物
        with transaction.atomic():

            # 创建事物的保存点
            save_point = transaction.savepoint()

            try:
                # 保存订单记录
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal("0"),
                    freight=Decimal("10.00"),
                    pay_method=pay_method,
                    status=status

                )

                # 2.修改sku的库存和销量
                # 创建redis连接
                redis_conn = get_redis_connection('carts')

                # 获取hash和set数据
                redis_dict = redis_conn.hgetall('carts_%s'%user.id)
                selected_ids = redis_conn.smembers('selected_%s'%user.id)
                # 定义一个字典用来包装购物车的商品id和count
                cart_dict = {}

                # 遍历set集合包装数据
                for sku_id_bytes in selected_ids:
                    # 取出商品的 id 和 count
                    cart_dict[int(sku_id_bytes)] = int(redis_dict[sku_id_bytes])

                for sku_id in cart_dict:

                    while True:
                        # 一次只查询出一个模型(减少缓存问题)
                        sku = SKU.objects.get(id=sku_id)
                        # 获取用户此商品要购买的数量
                        buy_count = cart_dict[sku_id]
                        # 定义两个变量来记录当前sku的原本库存和销量
                        origin_stock = sku.stock
                        origin_sales = sku.sales
                        # 判断当前要购买的商品库存是否充足
                        if buy_count > origin_stock:
                            # 库存不足就回滚
                            transaction.savepoint_rollback(save_point)
                            # 如果不足，提前响应
                            return http.JsonResponse({'code':RETCODE.SERVERERR,'errmsg':'库存不足'})
                        # 如果能购买，计算新的库存和销量
                        new_stock = origin_stock - buy_count
                        new_sales = origin_sales + buy_count
                        # 修改sku模型库存和销量
                        # sku.stock = new_stock
                        # sku.sales = new_sales
                        # sku.save()

                        # 乐观锁
                        result = SKU.objects.filter(id=sku_id,stock=origin_stock).update(stock=new_stock,sales=new_sales)

                        if result == 0:
                            continue

                        # 修改spu模型的销量
                        spu = sku.spu
                        spu.sales += buy_count
                        spu.save()


                        # 4.保存订单中的商品记录

                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=buy_count,
                            price=sku.price)

                        # 累加商品总数量
                        order.total_count += buy_count
                        # 累加商品总价
                        order.total_amount += (sku.price * buy_count)

                        break
                # 运费
                order.total_amount += order.freight
                order.save()

            except Exception:
                transaction.savepoint_rollback(save_point)
                return http.JsonResponse({'code':RETCODE.DBERR,'errmsg':'下单失败'})

            else:
                # 提交事物
                transaction.savepoint_commit(save_point)


                # 删除已结算的的购物车数据
                pl = redis_conn.pipeline()
                pl.hdel('carts_%s'%user.id,*selected_ids)
                pl.delete('selected_%s'%user.id)

                pl.execute()


        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'下单成功','order_id':order_id})


class OrderSuccessView(LoginRequiredMixin,View):
    """提交订单成功的界面"""
    def get(self,request):
        # 接收查询参数
        query_dict = request.GET
        order_id = query_dict.get('order_id')
        payment_amount = query_dict.get('payment_amount')
        pay_method = query_dict.get('pay_method')
        # 校验
        try:
            OrderInfo.objects.get(order_id=order_id,pay_method=pay_method,total_amount=payment_amount)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息有误')
        # 包装模板要进行渲染的数据
        context = {
            'order_id':order_id,
            'pay_method':pay_method,
            'payment_amount':payment_amount
        }
        # 响应
        return render(request,'order_success.html',context)


class AllOrder(LoginRequiredMixin,View):
    '''全部订单页面展示'''
    def get(self,request):
        return render(request,'user_center_order.html')



