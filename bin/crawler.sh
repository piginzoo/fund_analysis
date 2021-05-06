#!/bin/bash

if [ "$1" == "" ]
then
    echo "从天天基金爬取基金日交易数据："
    echo "bin/crawler.sh --code <基金代码>  --data <trade:日交易|info:相关信息> "
    echo "如：bin/crawler.sh --code 161725 --data info"
    echo "如：bin/crawler.sh --data trade"
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
python -m fund_analysis.crawler.main $*