#!/bin/bash
echo "=================="
echo "  基金利润计算"
echo "=================="

if [ "$1" == "" ]
then
    echo "计算真实的投资计划的收益率："
    echo "bin/profit.sh --code <基金代码> --plan <定投计划问题>"
    echo "如：bin/profit.sh --code 001938 --plan data/plan/jq_001938.txt"
    exit
fi

python -m fund_analysis.analysis.plan_profit $*