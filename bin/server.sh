#!/bin/bash
echo "=================="
echo "  基金定投分析"
echo "=================="

if [ "$1" = "stop" ]; then
    echo "停止 Web 服务"
    ps aux|grep fund_analysis|grep -v grep|awk '{print $2}'|xargs kill -9
    exit
fi

python -m fund_analysis.web.server>logs/log.txt 2>&1 &