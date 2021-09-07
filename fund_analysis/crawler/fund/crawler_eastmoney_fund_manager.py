# 导入需要的模块
import collections
import json

from bs4 import BeautifulSoup

from fund_analysis.bo.fund_manager import FundManager
from fund_analysis.crawler.crawler import Crawler
from fund_analysis.tools import utils
from fund_analysis.tools.utils import *

logger = logging.getLogger(__name__)
Manager = collections.namedtuple('Manager', ['start', 'end', 'manager', 'period', 'earn'])


class EastmoneyFundManagerCrawler(Crawler):
    """
    单独爬取一下最新的基金经理，
    参考：https://github.com/XDTD/fund_crawler
    http://fund.eastmoney.com/pingzhongdata/000001.js
    公司列表(Github上直接打开好像会提示not found,复制到浏览器上方直接进入即可)：http://fund.eastmoney.com/js/jjjz_gs.js
    基金列表：http://fund.eastmoney.com/js/fundcode_search.js
    基金信息1：http://fund.eastmoney.com/pingzhongdata/'+code+'.js‘
            其中,code为6位整数，如000001的URL位=为http://fund.eastmoney.com/pingzhongdata/000001.js
    基金信息2:http://fund.eastmoney.com/f10/tsdata_'+code+'.html'，同上
    基金经理信息:http://fundf10.eastmoney.com/jjjl_'+code+'.html',同上
    """

    def __get_content(self, url):
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text

    def crawle_one(self, code, force=False, period=None):
        manager = self.get_first_fund_manager(code)

        if not manager: return

        session = utils.connect_database()
        fund_manager = session.query(FundManager).filter(FundManager.code == code).limit(1).first()

        if fund_manager:
            logger.debug("基金%s的基金经理信息存在，删除它",code)
            session.delete(fund_manager)
            session.commit()

        fund_manager = FundManager()
        fund_manager.code = code
        fund_manager.manager = manager.manager
        fund_manager.start = manager.start
        fund_manager.end = manager.end
        fund_manager.period = manager.period
        fund_manager.earn = manager.earn

        session.add(fund_manager)
        session.commit()

    def get_manager(self, code):
        """
        从基金信息里扒拉出来，它的对应的基金经理的信息，
        不过这个虽然是在职的，但是没有任职时间，所以这个方法暂做保留把
        """
        response = self.__get_content('http://fund.eastmoney.com/pingzhongdata/' + code + '.js')

        manager_list = response.get('Data_currentFundManager', None)
        if manager_list is None or len(manager_list) == 0:
            logger.warning("找不到基金经理")
            return None

        for manager in manager_list:
            manager = json.loads(manager)[0]
            print("基金[%s]经理：#%r %s 管理时间%s 基金规模%s" %
                  (code,
                   manager['id'],
                   manager['name'],
                   manager['workTime'],
                   manager['fundSize']))

    def get_first_fund_manager(self, code):
        """
        从基金经理页，只取第一个，即在任的基金经理
        起始期,截止期,基金经理,任职期间,任职回报
        """
        response = self.__get_content("https://fundf10.eastmoney.com/jjjl_{}.html".format(code))
        soup = BeautifulSoup(response, 'html.parser')
        results = soup.select(".detail .txt_cont .boxitem table tbody tr")
        if results is None or len(results) == 0:
            return None
        manager = results[0]
        tds = manager.find_all('td')
        if len(tds) != 5:
            logger.warning("列数不够5个：起始期,截止期,基金经理,任职期间,任职回报：%d", len(tds))
            return None
        Manager = collections.namedtuple('Manager', ['start', 'end', 'manager', 'period', 'earn'])

        return Manager(start=tds[0].text,
                       end=tds[1].text,
                       manager=tds[2].text,
                       period=tds[3].text,
                       earn=tds[4].text)