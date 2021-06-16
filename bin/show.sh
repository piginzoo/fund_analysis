#!/bin/bash
echo "=================="
echo "  显示基金信息"
echo "=================="

if [ "$1" == "" ]
then
    echo "显示单只基金的信息："
    echo "bin/syow.sh --code <基金代码>"
    echo "如：bin/show.sh --code 519778"
    exit
fi

echo " <基金 $2>：$*"
python -m fund_analysis.analysis.calculate_show $*