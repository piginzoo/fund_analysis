import logging

from jqdatasdk import auth

from fund_analysis.tools import utils

logger = logging.getLogger(__name__)

def login():
    conf = utils.load_config()
    uid = str(conf['jqdata']['uid'])
    pwd = conf['jqdata']['pwd']  # 账号是申请时所填写的手机号；密码为聚宽官网登录密码，新申请用户默认为手机号后6位
    logger.info("用户名:%s,密码：%s", uid, pwd)
    auth(uid, pwd)
    logger.info("登录到jqdata成功")


def get_market_code(code):
    """
    所有沪市股票代码都是60开头的。
    深市主板股票是000和001开头的，
    深市中小板股票是002开头的，
    深市创业板股票是300开头的,
    创业板股票代码区间为：300000-399999,
    ------------------------------------------------
    交易市场	    代码后缀	示例代码	        证券简称
    上海证券交易所	.XSHG	'600519.XSHG'	贵州茅台
    深圳证券交易所	.XSHE	'000001.XSHE'	平安银行
    中金所	    .CCFX	'IC9999.CCFX'	中证500主力合约
    大商所	    .XDCE	'A9999.XDCE'	豆一主力合约
    上期所	    .XSGE	'AU9999.XSGE'	黄金主力合约
    郑商所	    .XZCE	'CY8888.XZCE'	棉纱期货指数
    上海期货交易所	.XINE	'SC9999.XINE'	原油主力合约
    :return:
    """
    if code.startswith('60'): return code + ".XSHG"
    if code.startswith('000'): return code + ".XSHE"
    if code.startswith('001'): return code + ".XSHE"
    if code.startswith('002'): return code + ".XSHE"
    if int(code)>=300000 and int(code)<400000: return code + ".XSHE"
    return code + ".XSHG"
