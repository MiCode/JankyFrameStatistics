[中文]

1. 本项目是用来分析手机卡顿时长的，帧绘制耗时大于100ms视作卡顿. 由MIUI团队(www.miui.com) 发起并贡献第一批代码，遵循NOTICE文件所描述的开源协议，
   今后为MiCode社区(www.micode.net) 拥有，并由社区发布和维护。

2. 用法:
    (只支持linux 终端中执行)
   (1) 开始抓取数据:
       执行 bash runDump.sh [参数1] start [参数2]
       参数1: 手机 serial number(adb devices 获取)
       参数2: 抓取数据间隔(s)
       示例: bash runDump.sh f13dacb5 start 1000
   (2) 停止抓取数据:
       执行 bash runDump.sh [参数1] stop
       参数1: 手机 serial number(adb devices 获取)
       示例: bash runDump.sh f13dacb5 stop
   (3) 分析结果:
       第(2)步后, 会在当前目录下生成graphic文件夹
       执行 python start_analysis.py -d [参数]
       参数: log文件路径
       示例: python start_analysis.py -d graphic
   (4) 查看结果:
       第(3)步后,在graphic文件夹中生成文本文件:caton_time

[English]
for static jank frame from graphicstatistic

