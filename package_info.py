# coding:utf-8

###############################################################################
#
#
# PackageInfo - 解析某一应用卡顿相关数据的工具类.
#
# Copyright 2017, YanHao, yanhao@xiaomi.com
#

# Parameters.
PACKAGE = "Package:"  # Google输出日志中Package信息标识
SINCE = "Stats since:"  # Google输出日志中Stats since信息标识
TOTAL_FRAMES = "Total frames rendered:"  # Google输出日志中Total frames rendered信息标识
CATON_FRAMES = "HISTOGRAM:"  # Google输出日志中HISTOGRAM信息标识
CATON_METRIC_SCALE = 100  #取100ms卡顿场景
PARSE_NOT_FOUND = ""


class PackageInfo:
    """解析某一应用卡顿数据的工具类.

     属性:
         package_name: 用于记录Package信息
         package_since: 用于记录Stats since信息
         caton_time: 用于记录超过100ms的卡顿时长
         total_frame: 用于记录总绘制帧数
         file_num: 文件序号
    """

    def __init__(self, package_name, package_since, caton_time=0, total_frame=0, file_num=0):
        """初始化PackageInfo."""
        self.package_name = package_name
        self.package_since = package_since
        self.caton_time = caton_time
        self.total_frame = total_frame
        self.file_num = file_num


    @staticmethod
    def parse_line(line):
        """解析一行日志并完成提取.

        参数:
            line: 需解析的某一行日志.

        返回值:
            解析结果

        """
        if not line or not line.strip().split(':')[1]:
            return ''
        return line.strip().split(':')[1].strip()


    @staticmethod
    def parse_since(since_str):
        """解析 status since 信息.

        参数:
            since_str: 需解析的某一字符串.

        返回值:
            since_time：Stats since信息对应的时间戳，单位纳秒

        """
        since_time = PARSE_NOT_FOUND
        if since_str is None or len(since_str) <= len(SINCE):
            return since_time
        if cmp(since_str[0:len(SINCE)], SINCE) == 0:
            temp = since_str.split(":")[1].strip(' ')
            since_time = temp[0:temp.find("ns")]

        return str(since_time)

    @staticmethod
    def parse_total_frame(total_frame_str):
        """解析总绘制帧数.

        参数:
            total_frame_str: 需解析的某一字符串.

        返回值:
            解析结果:总绘制帧数

        """
        temp_total_frame = 0
        if total_frame_str is None or len(total_frame_str) <= len(TOTAL_FRAMES):
            return PARSE_NOT_FOUND
        if cmp(total_frame_str[0:len(TOTAL_FRAMES)], TOTAL_FRAMES) == 0:
            temp_total_frame = PackageInfo.parse_line(total_frame_str)
        else:
            return PARSE_NOT_FOUND
        return str(temp_total_frame)

    @staticmethod
    def parse_caton(caton_str):
        """解析 卡顿时长.

        参数:
            caton_str: 需解析的某一字符串.

        返回值:
            caton_time：超过100ms的卡顿时长

        """
        temp_caton_time = 0
        if caton_str is None or len(caton_str) <= len(CATON_FRAMES):
            return PARSE_NOT_FOUND

        if cmp(caton_str[0:len(CATON_FRAMES)], CATON_FRAMES) == 0:
            cols = caton_str.split(' ')
            for col in cols:
                item = col.split('=')
                if len(item) == 2:
                    temp = item[0].strip(' ')
                    item_time = int(temp[0:temp.find("ms")])
                    if int(item_time) >= CATON_METRIC_SCALE:
                        temp_caton_time = temp_caton_time + int(item_time) * int(item[1])
        else:
            return PARSE_NOT_FOUND
        return str(temp_caton_time)

    def subtract(self, pkg_info):
        """实现 PackageInfo 类型之间的减法.
        
        调用者作被减数,参数作减数.

        参数:
            pkg_info: 减数.

        返回值:
            True：成功
            False:失败

        """
        if pkg_info is None:
            return False

        if self.package_since > pkg_info.package_since \
            or self.total_frame < pkg_info.total_frame \
                or self.caton_time < pkg_info.caton_time:
            print "package subtract not valid"
            return False
        self.total_frame = self.total_frame - pkg_info.total_frame
        self.caton_time = self.caton_time - pkg_info.caton_time
        return True

    def combine(self, pkg_info):
        """实现 PackageInfo 类型之间的加法.

        参数:
            pkg_info: 加数.

        返回值:
            True：成功
            False:失败

        """
        if pkg_info is None:
            return False
        self.total_frame = self.total_frame + pkg_info.total_frame
        self.caton_time = self.caton_time + pkg_info.caton_time
        return True

    def dump(self):
        """打印分析的卡顿数据."""
        print "package:" + self.package_name + ",totalFrame:" + str(self.total_frame) \
              + ",caton(100ms):" + str(self.caton_time)
