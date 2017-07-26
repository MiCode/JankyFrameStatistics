#define LOG_TAG "graphicstats"

#include <algorithm>
#include <chrono>
#include <thread>

#include <android-base/file.h>
#include <android-base/stringprintf.h>
#include <android-base/unique_fd.h>
#include <binder/IServiceManager.h>
#include <binder/Parcel.h>
#include <binder/ProcessState.h>
#include <binder/TextOutput.h>
#include <utils/Log.h>
#include <utils/Vector.h>

#include <fcntl.h>
#include <getopt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/poll.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/types.h>
#include <signal.h>
#include <unistd.h>

#include <string>
#include <cstring>

using namespace android;
using android::base::StringPrintf;
using android::base::unique_fd;
using android::base::WriteFully;

#define TIMEOUT 10
#define DEFAULT_ALARM_DURATION 1800
//标示是否有定时获取绘制信息
static bool g_alarmSet=false;
//定时的时间间隔，以s为单位，执行时设置参数
//默认为1800s，即半小时
static int g_alarmDuration=DEFAULT_ALARM_DURATION;
//标示第num次获取应用绘制信息
static int g_num = 0;
sp<IServiceManager> g_sm;

//调用android标准接口获得应用每帧的绘制信息
//输入参数sm, serviceManager, 通过它找到获取绘制信息的接口
//输入参数fd, 文件描述符，将获得的信息存储到这个文件描述符指向的文件
int dumpsysGraphics(int fd) {
	String16 service_name = String16("graphicsstats");
	Vector<String16> args;
	sp<IBinder> service = g_sm->checkService(service_name);
	ALOGD("DUMP GRAPHICS START");
	if (service != NULL) {
		int sfd[2];

		if (pipe(sfd) != 0) {
			aerr << "Failed to create pipe to dump service info for "
				<< ": " << strerror(errno) << endl;
			return 0;
		}

		unique_fd local_end(sfd[0]);
		unique_fd remote_end(sfd[1]);
		sfd[0] = sfd[1] = -1;

        // dump blocks until completion, so spawn a thread..
		std::thread dump_thread([=, remote_end { std::move(remote_end) }]() mutable {
			int err = service->dump(remote_end.get(), args);
                // It'd be nice to be able to close the remote end of the socketpair before the dump
                // call returns, to terminate our reads if the other end closes their copy of the
                // file descriptor, but then hangs for some reason. There doesn't seem to be a good
                // way to do this, though.
			remote_end.clear();

			if (err != 0) {
				aerr << "Error dumping service info: (" << strerror(err) << ") "
					<< endl;
            }
		});

		auto timeout = std::chrono::seconds(TIMEOUT);
		auto start = std::chrono::steady_clock::now();
		auto end = start + timeout;

		struct pollfd pfd = {
		    .fd = local_end.get(),
		    .events = POLLIN
		};

		bool timed_out = false;
		bool error = false;
		while (true) {
            // Wrap this in a lambda so that TEMP_FAILURE_RETRY recalculates the timeout.
			auto time_left_ms = [end]() {
				auto now = std::chrono::steady_clock::now();
				auto diff = std::chrono::duration_cast<std::chrono::milliseconds>(end - now);
				return std::max(diff.count(), 0ll);
			};

			int rc = TEMP_FAILURE_RETRY(poll(&pfd, 1, time_left_ms()));
			if (rc < 0) {
				aerr << "Error in poll while dumping service " << service_name << " : "
					<< strerror(errno) << endl;
				error = true;
				break;
			} else if (rc == 0) {
				timed_out = true;
				break;
			}

			char buf[4096];
			rc = TEMP_FAILURE_RETRY(read(local_end.get(), buf, sizeof(buf)));
			if (rc < 0) {
				aerr << "Failed to read while dumping service " << service_name << ": "
					<< strerror(errno) << endl;
				error = true;
				break;
			} else if (rc == 0) {
                // EOF.
				break;
			}

			if (!WriteFully(fd, buf, rc)) {
				aerr << "Failed to write while dumping service " << service_name << ": "
					<< strerror(errno) << endl;
				error = true;
				break;
			}
		}

		if (timed_out) {
			aout << endl << "*** SERVICE DUMP TIMEOUT EXPIRED ***" << endl << endl;
		}

		if (timed_out || error) {
			dump_thread.detach();
		} else {
			dump_thread.join();
		}
	}
	return 0;
}


int setAlarm(int sec);
//定时唤醒去处理任务，获取应用帧绘制信息并且设置下一次处理任务时间
void alarmHandler(int ID){
	ALOGD("handler alram");
	g_num++;
	g_alarmSet = false;
	char file[256] ;
	snprintf(file, 256, "/sdcard/graphic/graphic%d", g_num);
	int fd = open(file, O_CREAT | O_RDWR);
	if (fd > 0) {
		dumpsysGraphics(fd);
	    close(fd);
	}
	setAlarm(g_alarmDuration);
}


//设置定时任务
//输入参数sec,标示从现在起多长时间后执行任务
int setAlarm(int sec) {
	if (g_alarmSet) {
		ALOGE("alarm already set");
		return 0;
	}
	struct itimerval tick;
	int ret = 0 ;
	signal(SIGALRM, alarmHandler);
	ALOGE("setalarm %d", sec);


	tick.it_value.tv_sec = sec;
	tick.it_value.tv_usec =0;
	ret = setitimer(ITIMER_REAL , &tick, NULL);//ITIMER_REAL
	if (ret == 0) {
		g_alarmSet = true;
	}else {
		ALOGE("set error %d", ret);
	}
	return ret;
}

int main(int argc, char* argv[]) {
	signal(SIGPIPE, SIG_IGN);
	g_sm = defaultServiceManager();
	fflush(stdout);
	if (g_sm == NULL) {
		ALOGE("Unable to get default service manager!");
		aerr << "dumpsys: Unable to get default service manager!" << endl;
		return -1;
	}

	g_alarmDuration = DEFAULT_ALARM_DURATION;
	for (int i = 1;i < argc; i++) {
		if (strcmp(argv[i], "-t") == 0 && i < (argc-1)) {
			g_alarmDuration = atoi(argv[i+1]);
			i++;
			continue;
		}
	}
	//获取测试开始时的应用绘制信息
	alarmHandler(0);
	//设置定时获取应用绘制信息
	setAlarm(g_alarmDuration);

	while(1) {
		sleep(g_alarmDuration);
	}
}
