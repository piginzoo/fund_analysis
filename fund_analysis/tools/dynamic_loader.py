from pkgutil import walk_packages
import importlib
import logging
import inspect

from fund_analysis.analysis.base_calculator import BaseCalculator
from fund_analysis.tools import utils

logger = logging.getLogger(__name__)


def get_validator(class_name, validtor_dict):
    if class_name is None: return None

    if class_name.find("(") != -1:
        # 例如：KeyValueValidator('签发机关')
        if class_name.find("(") == -1:
            logger.warning("校验器命名不合法：%s", class_name)
            return None
        pure_class_name = class_name[:class_name.find("(")]
        params = class_name[class_name.find("(") + 1:class_name.find(")")]

        if params.strip()=="":
            params=[]
        else:
            params = params.split(",")  # 支持多个参数，逗号分隔，如 KeyValueValidator('签发机关',3)

        validtor_class = validtor_dict.get(pure_class_name, None)

        if validtor_class is None:
            logger.warning("无法找到预配置类：byname= %s",pure_class_name)
            return None

        try:
            params = convert_params(validtor_class,params) # 读取构造函数的类型，并做类型转换
            return validtor_class(*params)
        except:
            logger.exception("动态加载校验类失败：%r，参数：%r", validtor_class, params)
            return None
    else:
        validtor_class = validtor_dict.get(class_name, None)
        try:
            return validtor_class()
        except:
            logger.exception("动态加载无参数校验类失败：%r", validtor_class)
            return None


# 对构造函数的参数做类型转换，目前仅支持int，未来可以自由扩充
# 注意！构造函数的参数一定要标明类型，如 name:int
def convert_params(clazz, param_values):
    # logger.debug("准备转化%r的参数：%r",clazz,param_values)
    full_args = inspect.getfullargspec(clazz.__init__)
    annotations = full_args.annotations
    arg_names = full_args.args[1:]  # 第一个是self，忽略
    new_params = []
    for i, value in enumerate(param_values):

        arg_name = arg_names[i]
        arg_type = annotations.get(arg_name, None)
        if arg_type and value and arg_type == int:
            logger.debug("参数%s的值%s转化成int",arg_name,value)
            value = int(value)
        new_params.append(value)

    return new_params


def dynamic_load_classes(parent_class):
    classes = []
    module_name = ".".join(parent_class.__module__.split(".")[:-1]) # 得到父类的package名字,因为是文件颗粒度，所以要再向上寻找一个
    base_module = importlib.import_module(module_name) # 加载module

    # 遍历这个package中所有的类
    for _, name, is_pkg in walk_packages(base_module.__path__, prefix="{}.".format(module_name)):
        if is_pkg: continue

        # 导入每一个子package、类
        module = importlib.import_module(name)

        for name, obj in inspect.getmembers(module):

            # 只过滤这个父类的子类
            if not inspect.isclass(obj): continue
            if not issubclass(obj, parent_class): continue
            if obj == parent_class: continue
            classes.append(obj)

            # print(name, ",", obj)

    return classes


def dynamic_instantiation(class_def):
    objs = {}
    classes = dynamic_load_classes(class_def)
    for clazz in classes:
        # obj = clazz()
        # print(clazz.__name__)
        objs[clazz.__name__] = clazz
    return objs


# python -m fund_analysis.tools.dynamic_loader
if __name__ == "__main__":
    utils.init_logger()

    class_dict = dynamic_instantiation(BaseCalculator)
    logger.debug("所有的加载类：%r",class_dict)

