from celery import Celery
import os

# 告诉celery它里面需要用到的django配置文件在哪里
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")

#1. 创建Celery实例对象
celery_app = Celery('meiduo')

# 2.加载配置信息，指定中间人
celery_app.config_from_object('celery_tasks.config')
# 3.自动注册任务----当前celery只处理那些任务
# 复数形式---用列表
celery_app.autodiscover_tasks(['celery_tasks.sms',"celery_tasks.email"])