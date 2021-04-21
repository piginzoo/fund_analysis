import logging

from tqdm import tqdm

from fund_analysis import utils, crawler

FUND_LIST = "db/fund_list.db"

logger = logging.getLogger(__name__)


def load_fund_list():
    """
    "000001","HXCZHH","华夏成长混合","混合型","HUAXIACHENGZHANGHUNHE"
    :return:
    """
    with open(FUND_LIST, "r", encoding='utf-8') as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
    logger.debug("加载了%d行Fund数据", len(lines))
    return lines


def main():
    fund_list = load_fund_list()

    pbar = tqdm(total=len(fund_list))
    for i in range(len(fund_list)):
        fund_info = fund_list[i].split(",")
        fund_info = [f.replace("\"", "") for f in fund_info]
        try:
            crawler.main(fund_info[0])
        except:
            logger.info("爬取 [%s] : %s 失败！！！", fund_info[2], fund_info[0])
        logger.info("爬取 [%s] : %s", fund_info[2], fund_info[0])
        pbar.update(1)
    pbar.close()


# python -m fund_analysis.main
if __name__ == '__main__':
    utils.init_logger()
    main()
