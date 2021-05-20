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
