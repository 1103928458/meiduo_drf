from django.core.files.storage import Storage  # 自定义文件存储系统模块


class FastDFSStorage(Storage):
    """自定义文件存储系统"""

    def _open(self, name, model="rb"):
        """
        用于打开文件
        :param name:  要打开的文件名
        :param model: 文件打开模式
        :return: None
        """

    def _save(self,name,content):
        """
        使用fastDFS进行上传图片时就会调用此方法

        :param name: 要保存的文件名字
        :param content: 要保存的文件的内容
        :return: None    file_id
        """


    def url(self, name):
        """
        当使用imagefiled类型字段调用url属性时就会调用此方法拼接图片的绝对路径
        :param name: file_idg
        :return: 图片文件绝对路径
        """
        return "http://192.168.216.163:8888/"+name