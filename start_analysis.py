# coding:utf-8

###############################################################################
#
# 入口:开始分析
#
# Copyright 2017, YanHao, yanhao@xiaomi.com
#

import optparse
from graphic_result_file import GraphicResultFile
from graphic_statics import GraphicStatics

RESULT_DIR = '/result'
RESULT_FILE = 'caton_time'


if __name__ == '__main__':
    # 接收参数
    parser = optparse.OptionParser()
    parser.add_option('-d', '--directory', dest='log_dir', type='string')
    options, args = parser.parse_args()
    log_dir = options.log_dir

    # 开始分析帧率
    graphic_stats = GraphicStatics(log_dir)

    # 解析文件夹中的log文件
    graphic_stats.parse_dir()

    # 统计并打印结果
    result_list = graphic_stats.dump()

    # 将最终结果写入文件
    result_dir = log_dir + RESULT_DIR
    GraphicResultFile(result_dir, RESULT_FILE).transfer_to_file(result_list)
