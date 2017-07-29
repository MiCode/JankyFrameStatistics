# coding:utf-8

###############################################################################
#
# GraphicStatics - 分析卡顿数据.
# 分析并输出给定目录中的数据文件, 这些数据文件是用adb shell dumpsys graphicsstats命令生成好的,
# 这里只做分析计算和结果输出
#
# Copyright 2017, YanHao, yanhao@xiaomi.com
#

import os
import package_info as info
import package_statics

FILE_NAME_PREFIX = 'graphic'


class GraphicStatics:
    """主类:用于分析 adb shell dumpsys graphicsstats生成的结果并打印."""

    _CONFIG_THIRD_PART_APP = 'third_part_app.config'  # 配置文件:所有第三方app

    def __init__(self, directory):
        """初始化类 GraphicStatics."""
        self.__path = None  # log数据文件路径
        self.__file_num = 0  # log数据文件序号
        self.__package_info = dict()
        self.__third_app_list = []  # 第三方app列表

        if directory is None or not os.path.isdir(directory):
            raise Exception('错误的路径')
        else:
            self.__path = directory

        with open(self._CONFIG_THIRD_PART_APP) as third_part_apps:
            for line in third_part_apps.readlines():
                self.__third_app_list.append(line.strip('\n'))

    def parse_dir(self):
        """解析指定log文件夹中的数据."""
        for file in os.listdir(self.__path):
            if file.find(FILE_NAME_PREFIX) == 0:
                self.__file_num = self.__file_num + 1

        for i in range(1, self.__file_num + 1):
            file_num = self.__file_num + 1 - i
            file_name = self.__path + '/'+FILE_NAME_PREFIX + str(file_num)
            if not self.parse_file(file_name, file_num):
                print 'parse file ' + file_name + ' error'

    def parse_file(self, file_name, file_num):
        """分析指定log文件,提取卡顿相关数据.

        参数:
            file_name: 要分析的文件名.
            file_num: 文件序号.

        返回值:
            是否最后一个文件.

        """
        pkg_static = None
        print 'start parse:' + file_name
        if not os.path.isfile(file_name):
            print 'there is not the file:' + file_name
            return

        with open(file_name) as graphic_file:
            for line in graphic_file.readlines():
                if cmp(line[0:len(info.PACKAGE)], info.PACKAGE) == 0:
                    # 解析包名
                    temp_package = line.strip().split(':')[1].strip()
                    if self.__package_info.has_key(temp_package):
                        pkg_static = self.__package_info[temp_package]
                    else:
                        pkg_static = package_statics.PackageStatics(temp_package)
                    pkg_static.reset_state()
                if pkg_static:
                    # 解析包下的卡顿信息(卡顿时长,总帧数等)
                    ret = pkg_static.parse_info(line, file_num)
                    if ret:
                        self.__package_info[pkg_static.package_name] = pkg_static
                        pkg_static = None

        return True

    def dump(self):
        """打印结果.

        参数:
            无.

        返回值:
            返回最终分析结果.

        """
        total_result_list = [0]*3  # 全部app的统计结果
        third_result_list = [0]*3  # 第三方app的统计结果
        sys_result_list = [0]*3  # 系统app的统计结果
        result_list = []

        for (pkg, pkg_info) in self.__package_info.iteritems():
            pkg_info.dump()

            if pkg in self.__third_app_list:
                third_result_list[0] = third_result_list[0] + pkg_info.caton_time
                third_result_list[1] = third_result_list[1] + pkg_info.total_frame
            else:
                sys_result_list[0] = sys_result_list[0] + pkg_info.caton_time
                sys_result_list[1] = sys_result_list[1] + pkg_info.total_frame

        total_result_list[0] = sys_result_list[0] + third_result_list[0]
        total_result_list[1] = sys_result_list[1] + third_result_list[1]

        print '---------- Total Apps: ----------'
        print 'totalFrames:' + str(total_result_list[1])
        print 'totalCaton(100ms):' + str(total_result_list[0])
        print '---------- Third Part Apps: ----------'
        print 'thirdFrames:' + str(third_result_list[1])
        print 'thirdCaton(100ms):' + str(third_result_list[0])
        print '---------- System Apps: ----------'
        print 'sysFrames:' + str(sys_result_list[1])
        print 'sysCaton(100ms):' + str(sys_result_list[0])

        result_list.append(str(total_result_list[0]))
        result_list.append(str(third_result_list[0]))
        result_list.append(str(sys_result_list[0]))
        return result_list
