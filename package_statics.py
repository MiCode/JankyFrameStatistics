# coding:utf-8

###############################################################################
#
# PackageStatics - 保存分析同一应用的卡顿数据.
# 在原始数据中，同一个应用有很多绘制数据，通过这个类去保存，分析结果
#
# Copyright 2017, YanHao, yanhao@xiaomi.com
#

import package_info as info

# Parameters.
LAST_FILE_NUM = 1
IDLE = 0          # 空闲状态
TOTAL_FRAMES = 1  # 统计绘制帧数状态
CATON_TIME = 2    # 统计卡顿时长状态


class PackageStatics:
    """"分析某一应用卡顿数据的工具类.

    属性:
        package_name: 用于记录Package信息
    """
    def __init__(self, package_name):
        self.__package_dict = dict()  #保存数据中同一应用的绘制信息
        self.package_name = package_name
        self.__state = IDLE   #内部解析数据时使用的状态
        self.__cur_package = None  #解析时当前的应用绘制信息
        self.__last_file_num = 0  #表示上次解析的数据文件number
        self.__has_two_statics_one_file = False #标示一个文件是否有两个统计信息
        self.caton_time = 0    # 卡顿时长
        self.total_frame = 0    # 绘制总帧数

    def parse_info(self, line, file_num):
        """解析一行日志并完成提取'卡顿时长'和'绘制总帧数'.

        参数:
            line: 需解析的某一行日志.
            file_num: log文件序号

        返回值:
            解析结束返回True

        """
        if self.__state == IDLE:
            """解析log中Stats since"""
            since = info.PackageInfo.parse_since(line)
            if since != info.PARSE_NOT_FOUND:
                if self.__package_dict.has_key(long(since)) and file_num != LAST_FILE_NUM:
                    """the package since has exist, do not parse, wait over"""
                    self.__state = CATON_TIME
                elif not self.__package_dict.has_key(long(since)) and file_num == LAST_FILE_NUM:
                    """since the package is the last, do not parse, wait over"""
                    self.__state = CATON_TIME
                else:
                    """create new package info"""
                    self.__cur_package = info.PackageInfo(self.package_name,
                                                          package_since=long(since), file_num=file_num)
                    self.__state = TOTAL_FRAMES
        elif self.__state == TOTAL_FRAMES:
            """统计总绘制帧数."""
            total_frames = info.PackageInfo.parse_total_frame(line)
            if total_frames != info.PARSE_NOT_FOUND and self.__cur_package:
                self.__cur_package.total_frame = int(total_frames)
                self.__state = CATON_TIME
        elif self.__state == CATON_TIME:
            """统计卡顿绘制时长"""
            caton_time = info.PackageInfo.parse_caton(line)
            if caton_time != info.PARSE_NOT_FOUND:
                if self.__cur_package:
                    self.__cur_package.caton_time = int(caton_time)
                    if self.__package_dict.has_key(self.__cur_package.package_since) \
                            and file_num == LAST_FILE_NUM:
                        """减掉log文件中第一轮数据(测试前数据)"""
                        sub_success = self.__package_dict[self.__cur_package.package_since].subtract(self.__cur_package)
                        if not sub_success:
                            print 'Fail to remove the first round data'
                    elif not self.__package_dict.has_key(self.__cur_package.package_since):
                        """检查是否已经加入，如果没有再加入到字典中"""
                        self.__package_dict[self.__cur_package.package_since] = self.__cur_package
                    if self.__last_file_num != file_num:
                        self.__last_file_num = file_num
                    else:
                        """一个log文件中同一个包名的绘制信息出现多次"""
                        self.__has_two_statics_one_file = True
                self.reset_state()
                return True
        return False

    def reset_state(self):
        self.__cur_package = None
        self.__state = IDLE

    def statistic(self):
        """统计package的frame信息.

        参数:
            无

        返回值:
            total_frame: 总绘制帧数
            caton_time：卡顿时长
        """
        temp_total_frame = 0
        temp_caton_time = 0
        if not self.__has_two_statics_one_file:
            """如果不存在一个文件包含多个gaphic信息，将所有统计信息累加"""
            for (since, pkg) in self.__package_dict.iteritems():
                temp_total_frame = temp_total_frame + pkg.total_frame
                temp_caton_time = temp_caton_time + pkg.caton_time
        else:
            if len(self.__package_dict) == 2:
                """对于一个文件中包含多个同一个package的graphic信息，如果只有两个，做累加"""
                for (since, pkg) in self.__package_dict.iteritems():
                    temp_total_frame = temp_total_frame + pkg.total_frame
                    temp_caton_time = temp_caton_time + pkg.caton_time
            else:
                """如果有出现这样的情况，数据可能有些异常，需要人工统计!!!
                从目前来看，在测试过程中没有出现过此种情况
                虽然测试中没有出现过这种情况
                我们为了能够尽可能保证数据完整，打算选择绘制最多的统计"""
                print "do not static this situation"
                temp_pkg = None
                for (since, pkg) in self.__package_dict.iteritems():
                    if not temp_pkg:
                        temp_pkg = pkg
                    elif temp_pkg.total_frame < pkg.total_frame:
                        temp_pkg = pkg
                    print str(since)
                    pkg.dump()
                temp_total_frame = temp_pkg.total_frame
                temp_caton_time = temp_pkg.caton_time
        self.caton_time = temp_caton_time
        self.total_frame = temp_total_frame
        return temp_total_frame, temp_caton_time

    def dump(self):
        """打印结果."""
        (total, caton) = self.statistic()
        print "Package:" + self.package_name + " total_frames:" + str(total) \
              + " canton_time:" + str(caton)
