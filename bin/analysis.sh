#!/bin/bash

if [ "$1" == "" ]
then
    echo "分析所有的基金："
    echo "bin/analysis.sh --code <基金代码>  # 分析某一支"
    echo "bin/analysis.sh all               # 分析所有的基金"
    echo "如：bin/analysis.sh --code 161725"
    echo "如：bin/analysis.sh all"
    exit
fi

if [ "$1" == "all" ]
then
    echo "分析所有的基金..."
    python -m fund_analysis.analysis.analysis>logs/analysis.log 2>&1 &
    exit
fi

if [ "$1" == "stop" ]
then
    echo "停止爬虫..."
    ps aux|grep fund_analysis|grep -v grep|awk '{print $2}'|xargs kill -9
    exit
fi


echo "分析基金，代码：$*"
python -m fund_analysis.analysis.analysis $*