# coding:utf-8

###############################################################################
#
# GraphicResultFile - 将结果输出至文件
#
# Copyright 2017, YanHao, yanhao@xiaomi.com
#

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class GraphicResultFile:
    """文件类:用于保存最终结果."""
    _TITLES = ['全部app:   ', '第三方app: ', '系统app:   ']

    def __init__(self, dir, file):
        """初始化类 GraphicResultFile."""
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.__file = dir + '/' + file

    def transfer_to_file(self, data=''):
        """将输入内容保存至文件

        参数:
            data: 要保存的数据. 默认为''.

        返回值:
            无.

        """
        output = open(self.__file, 'w')
        for i in range(len(self._TITLES)):
            output.write(self._TITLES[i] + data[i] + '\n')

        output.close()
