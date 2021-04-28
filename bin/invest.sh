#!/bin/bash
echo "=================="
echo "  基金定投分析"
echo "=================="

if [ "$1" == "" ]
then
    echo "bin/invest.sh --code <基金代码> --start <定投开始日期> --end <定投结束日期> --period <day|week|month> --day <第几日>"
    echo "如：bin/invest.sh --code 519778 --start 2020-01-01 --end 2021-04-22 --period month --day 12"
    exit
fi

echo " <基金 $2>：$*"
python -m fund_analysis.invest.auto_invest $*