#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Title   : 模块
@File    :   __init__.py
@Author  : vincent
@Time    : 2020/8/28 4:53 下午
@Version : 1.0
'''
import io
import logging
import os

from flask import render_template, request, Flask, jsonify
from werkzeug.routing import BaseConverter

from fund_analysis.analysis.base_calculator import BaseCalculator
from fund_analysis.tools import utils
from fund_analysis.tools.dynamic_loader import dynamic_instantiation
from fund_analysis.tools.utils import start_capture_console, end_capture_console

base_path = os.getcwd()
template_path = os.path.join(base_path, "fund_analysis/web/templates")
static_path = os.path.join(base_path, "fund_analysis/web/static")


class RegexConverter(BaseConverter):
    def __init__(self, map, *args):
        self.map = map
        self.regex = args[0]


app = Flask('app',
            template_folder=template_path,
            static_folder=static_path,
            static_url_path="/static")
app.config['SECRET_KEY'] = '123456'  # os.urandom(32) <-- 不能随机，否则，不同gunicorn进程之间无法共享session了
app.jinja_env.variable_start_string = '[['  # 解决vue和flask的{{ }}的冲突问题=>[[ ]]
app.jinja_env.variable_end_string = ']]'
app.url_map.converters['regex'] = RegexConverter
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.debug = True

logger = logging.getLogger(__name__)


def init():
    class_dict = dynamic_instantiation(BaseCalculator)
    caculator_mapping = {}
    for _, clazz in class_dict.items():
        instance = clazz()
        caculator_mapping[instance.name()] = instance
    return caculator_mapping


CALCULATOR_MAPPING = init()


@app.route('/')
def index():
    return render_template("/index.html")


@app.route('/<regex(".*.html"):url>')
def html_request(url):
    return render_template(url)


@app.route('/execute', methods=['POST'])
def execute():
    request_data = request.get_json()
    logger.debug(request_data)
    calculator_name = request_data['calculator']
    command = request_data['command']
    logger.debug("需要运行的命令：%s %s", calculator_name, command)
    result, base64_images = run(calculator_name,command)
    return jsonify({'result': result, 'images': base64_images})


@app.route('/help', methods=['POST'])
def help():
    request_data = request.get_json()
    logger.debug(request_data)
    name = request_data['name']
    caculator = CALCULATOR_MAPPING.get(name, None)
    arg_parser = caculator.get_arg_parser()
    stream = io.StringIO()
    arg_parser.print_help(stream)
    help = stream.getvalue()
    stream.close()
    help_list = help.split("\n\n")[1:] # 去掉第一行，没啥用，还导致歧义
    help = "\n".join(help_list)
    return jsonify({'help': help})


@app.route('/list', methods=['POST'])
def list():
    return jsonify({'list': [k for k, v in CALCULATOR_MAPPING.items()]})


def run(calculator_name,command):
    """
    fund_analysis.analysis.calculate_alpha --code 009549 --type fund --period week --index 上证指数
    :return:
    """
    calculator = CALCULATOR_MAPPING.get(calculator_name,None)
    if calculator is None:
        raise ValueError("无效的计算命令："+calculator_name)

    try:
        io_stream, original_stdout, original_logger_stdout = start_capture_console()
        base64_images = calculator.main(command.strip().split(" "))
        result = end_capture_console(io_stream, original_stdout, original_logger_stdout)
    except Exception as e:
        result = end_capture_console(io_stream, original_stdout, original_logger_stdout)
        logger.debug(result)
        logger.exception("计算过程发生异常")
        return "发生异常：" + str(e),[]

    # result = "result"
    logger.debug("命令：[%s]\n%s", command, result)
    logger.debug("生成图片：[%d]张", len(base64_images))

    return result, base64_images


# python -m fund_analysis.web.server "fund_analysis.analysis.calculate_alpha --code 009549 --type fund --period week --index 上证指数"
# if __name__ == '__main__':
#     run(sys.argv[1])

if __name__ == '__main__':
    utils.init_logger()
    app.run()
