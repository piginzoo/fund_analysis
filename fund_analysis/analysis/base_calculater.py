import io
import logging

from fund_analysis.tools import utils
from fund_analysis.tools.utils import export_matplotlib_image_2_base64

logging.getLogger('matplotlib.font_manager').disabled = True
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)
class BaseCalculator(metaclass=ABCMeta):
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def plot(self, data):
        pass

    @abstractmethod
    def load_data(self, args):
        pass

    @abstractmethod
    def calculate(self, data):
        pass

    @abstractmethod
    def get_arg_parser(self):
        pass

    def parse_args(self, args=None):
        logger.debug("命令参数为：%r",args)
        if type(args) == str: args = args.split(" ")
        parser = self.get_arg_parser()
        args = parser.parse_args(args)
        return args

    def main(self, args, console=False):
        utils.init_logger()
        args = self.parse_args(args)
        data = self.load_data(args)
        result = self.calculate(data)
        plt = self.plot(result)

        # 图形展现
        if console:
            plt.show()
        else:
            base64_data = export_matplotlib_image_2_base64(plt)
            logger.debug("图片大小：%d", len(base64_data))
            return [base64_data]