from collections import namedtuple
from queue import Empty

from fund_analysis.analysis.calculate_TM import TMCalculater
from fund_analysis.analysis.calculate_show import ShowCalculater
from fund_analysis.tools.multi_processor import execute
from fund_analysis.tools.utils import init_logger

"""
明星基金：https://mp.weixin.qq.com/s/vrnpUMaocnKEAmIsVNSyNQ
这个是来验证，这篇文章中所提及的明星基金经理和他们的基金的TM模型结果
"""
star_funds = \
    {'005827': '易方达蓝筹精选',
     '110011': '易方达中小盘',
     '110022': '易方达消费行业',
     '110013': '易方达科翔',
     '110015': '易方达行业领先',
     '110027': '易方达安心回报A',
     '270002': '广发稳健增长A',
     '002939': '广发创新升级',
     '001763': '广发多策略',
     '000697': '汇添富全球移动互联',
     '519069': '汇添富价值精选A',
     '006113': '汇添富创新医药',
     '519068': '汇添富成长焦点',
     '002001': '华夏回报A',
     '002891': '华夏移动互联人民币',
     '006252': '富国消费主题A',
     '161005': '富国天惠精选成长A',
     '100060': '富国高新技术产业',
     '007340': '南方科技创新A',
     '202003': '南方绩优成长A',
     '000595': '嘉实泰和',
     '001044': '嘉实新消费',
     '003095': '中欧医疗健康A',
     '001938': '中欧时代先锋A',
     '166002': '中欧新蓝筹A',
     '166006': '中欧行业成长A',
     '166005': '中欧价值发现A',
     '163402': '兴全趋势投资',
     '163406': '兴全合润',
     '340005': '兴全合宜A',
     # '163415': '兴全商业模式优选',
     # '162605': '景顺长城鼎益',
     # '260101': '景顺长城优选',
     # '260116': '景顺长城核心竞争力A',
     # '260103': '景顺长城动力平衡',
     # '519772': '交银新生活力',
     # '519736': '交银新成长',
     # '519712': '交银阿尔法',
     # '000854': '鹏华养老产业',
     # '005812': '鹏华研究精选',
     # '040020': '华安升级主题',
     # '001714': '工银瑞信文体产业A',
     # '000251': '工银瑞信金融地产A',
     # '000831': '工银瑞信医疗保健行业',
     # '169104': '东方红睿满沪港深',
     # '003940': '银华盛世精选',
     # '180012': '银华富裕主题',
     # '001500': '泓德远见回报',
     # '001256': '泓德优选成长',
     # '001102': '前海开源国家比较优势A',
     # '000136': '民生加银策略精选A',
     # '001538': '上投摩根科技前沿',
     # '161903': '万家行业优选',
     # '000336': '农银汇理研究精选'
     }
tm_calculator = TMCalculater()
basic_calculator = ShowCalculater()

Result = namedtuple('Result', ['code', 'name', 'start', 'year', 'alpha', 'beta2', 'profit', 'aagr', 'withdraw'])
import logging

logger = logging.getLogger(__name__)

init_logger()


def format(results):
    logger.debug(
        "=====================================================================================================================")

    logger.debug(
        "| {1:^8} | {2:{0}^15} | {3:^8} | {4:^4} | {5:^6} |  {6:^6} |  {7:^4} |  {8:^4} |  {9:^4} |".format(
            chr(12288), "Code", "名称", "开始", "年限", "α", "β2", "总收益", "年化收益", "最大回撤"
        )
    )

    for r in results:
        # print(r.code,
        #       r.name,
        #       r.alpha,
        #       r.beta2,
        #       r.profit * 100,
        #       r.aagr * 100,
        #       r.withdraw * 100
        #       )
        logger.debug(
            "---------------------------------------------------------------------------------------------------------------------")

        str_r = "| {1:^8} | {2:{0}^15} | {3:^8} | {4:^6.1f} | {5:^6.2%} |  {6:^6.2%} |  {7:^6.2%} |  {8:^8.2%} |  {9:^8.2%} |".format(
            chr(12288),
            r.code,
            r.name,
            r.start,
            r.year,
            r.alpha,
            r.beta2,
            r.profit,
            r.aagr,
            r.withdraw
        )
        logger.debug(str_r)
    logger.debug(
        "=====================================================================================================================")


def process(data, id, queue):
    code, name = data
    args = "--code {} --type fund --period week --index 上证指数".format(code)
    x, y, pred, alpha, beta1, beta2 = tm_calculator.process(args)
    args = "--code {}".format(code)
    data, index_close_price, max_withdraw, start, year, aagr, total_profit = \
        basic_calculator.process(args)
    logger.debug("[%s],α=%.4f,β2=%.4f", code, alpha, beta2)
    logger.debug(
        "-----------------------------------------------------------------------------------------------------")
    queue.put(Result(
        code,
        name,
        start,
        year,
        alpha,
        beta2,
        total_profit,
        aagr,
        max_withdraw))


# python -m fund_analysis.projects.star_funds
if __name__ == '__main__':

    queue = execute(star_funds, worker_num=4, function=process)
    results = []
    while True:
        try:
            # https://my.oschina.net/yangyanxing/blog/296052
            data = queue.get_nowait()
            results.append(data)
        except Empty:
            logger.info("队列已空，全部取完！")
            break
    format(results)
