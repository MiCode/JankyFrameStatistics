#!/usr/bin/env bash
ANDROID_SERIAL=$1    # Device serial number.
TIME=$3    # The time of every round.


# Kill a process by name.
kill_process() {
    if [ -n "$1" ];then
        adb -s $ANDROID_SERIAL shell ps | grep $1 | awk '{print $2}' | xargs adb -s $ANDROID_SERIAL shell kill
    else
        echo "Parameter error, when trying to kill the process."
    fi
}

if [ x"$2" == x"start" ]; then
	echo "Start testing."
	kill_process graphic_dump
	adb -s $ANDROID_SERIAL push graphic_dump /data/local/tmp/graphic_dump
	adb -s $ANDROID_SERIAL shell chmod 755 /data/local/tmp/graphic_dump
	adb -s $ANDROID_SERIAL shell mkdir /sdcard/graphic
	adb -s $ANDROID_SERIAL shell "./data/local/tmp/graphic_dump -t $TIME &" &
	[ -n "$(adb -s $ANDROID_SERIAL shell ps | grep graphic_dump)" ] && \
	    echo "Graphic_dump is running." || echo "Graphic_dump is not running, please retry."

elif [ x"$2" == x"stop" ]; then
	echo "Stop testing, collect data."
    kill_process graphic_dump
	[ -d "graphic" ] && rm -rf graphic
	adb -s $ANDROID_SERIAL pull /sdcard/graphic graphic
	adb -s $ANDROID_SERIAL shell rm -rf /sdcard/graphic/*
else
    echo "Please enter the correct instruction."
fi