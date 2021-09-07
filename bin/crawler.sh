#!/bin/bash

if [ "$1" == "" ]
then
    echo "从天天基金、或者JQData，爬取交易数据："
    echo "bin/crawler.sh --code <代码> --type <stock|fund> --sub_type <trade:日交易|info:相关信息> [--force]"
    echo "爬取基金："
    echo "如：bin/crawler.sh --code 161725 --type fund --sub_type info"
    echo "如：bin/crawler.sh --type fund  --sub_type trade "
    echo "爬取股票："
    echo "如：bin/crawler.sh --code 300122 --type stock"
    echo "如：bin/crawler.sh --code 300122 --type stock --period 120m"

    exit
fi

if [ "$1" == "all" ]
then
    echo "爬取所有的基金..."
    python -m fund_analysis.crawler.main>logs/crawler.log 2>&1 &
    exit
fi

if [ "$1" == "stop" ]
then
    echo "停止爬虫..."
    ps aux|grep fund_analysis|grep -v grep|awk '{print $2}'|xargs kill -9
    exit
fi


echo "爬取 <代码>，代码：$*"
python -m fund_analysis.crawler.main $*