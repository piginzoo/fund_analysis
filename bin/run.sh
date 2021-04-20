#!/bin/bash

if [ "$1" == "" ]
then
    echo "bin/run.sh --code <基金代码>"
    echo "如：bin/run.sh --code 161725"
    exit
fi

python -m fund_analysis.crawler $*