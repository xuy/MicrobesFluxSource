#!/bin/bash
# Check Daemon, poor man's daemontools
ps -ef | grep -v grep | grep watchdog.py > /dev/null 2>&1
if [ $? -eq 1 ]
then
echo "Automatically re-start watchdog"
/home/research/xuy/script/watchdog.py
fi
