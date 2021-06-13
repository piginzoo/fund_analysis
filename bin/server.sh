#!/bin/bash
if [ "$1" = "stop" ]; then
    echo "停止 Web 服务"
    ps aux|grep fund_analysis|grep -v grep|awk '{print $2}'|xargs kill -9
    exit
fi


if [ "$1" = "debug" ]; then
    echo "调试模式..."
    python -m fund_analysis.web.server
    exit
fi


echo "启动服务器..."
nohup python -m fund_analysis.web.server>logs/log.txt 2>&1 &