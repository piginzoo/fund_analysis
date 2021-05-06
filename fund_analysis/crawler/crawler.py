import logging
from datetime import time

from tqdm import tqdm

from fund_analysis.tools import utils

logger = logging.getLogger(__name__)


class Crawler():
    def crawle_one(self, code):
        pass

    def crawle_all(self, code, num):
        if code:
            self.crawle_one(code)
            return

        fund_code_list = utils.load_fund_list()

        pbar = tqdm(total=min(num, len(fund_code_list)))
        counter = 0
        error = 0
        start = time.time()
        for fund in fund_code_list:

            try:
                success = self.crawle_one(fund.code)
                if not success: error += 1
            except:
                logger.exception("爬取 [%s] 失败...", fund.code)
                error += 1
                continue

            counter += 1
            if counter > num: break

            # time.sleep(1)  # random.random())
            pbar.update(1)

        pbar.close()
        end = time.time()

        logger.info("合计爬取[%d]条，[%d]失败，[%d]成功，平均耗时：%.2f 秒/条",
                    counter,
                    error,
                    counter - error,
                    (end - start) / counter)
