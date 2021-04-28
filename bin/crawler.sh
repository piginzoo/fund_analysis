#!/bin/bash

if [ "$1" == "" ]
then
    echo "bin/run.sh --code <基金代码> | all"
    echo "如：bin/run.sh --code 161725"
    exit
fi

if [ "$1" == "all" ]
then
    echo "爬取所有的基金..."
    python -m fund_analysis.crawler.main>log/log.txt 2>&1 &
    exit
fi

if [ "$1" == "stop" ]
then
    echo "停止爬虫..."
    ps aux|grep fund_analysis|grep -v grep|awk '{print $2}'|xargs kill -9
    exit
fi


echo "爬取 <基金代码>，代码：$*"
python -m fund_analysis.crawler.crawler $*