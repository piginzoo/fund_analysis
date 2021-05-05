import argparse
import logging

from fund_analysis.crawler import helper_jqdata
from fund_analysis.tools.utils import init_logger

logger = logging.getLogger(__name__)


def main(code):
    helper_jqdata.get_fund_info(code)


# 主程序
# python -m fund_analysis.crawler_fund --code 161725
if __name__ == "__main__":
    init_logger()
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', '-c', type=str)
    args = parser.parse_args()
    if not args.code:
        logger.error("基金代码为空: --code xxxx")
        exit()
    main(args.code)
