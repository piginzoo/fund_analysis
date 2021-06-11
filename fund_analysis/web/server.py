#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Title   : 模块
@File    :   __init__.py
@Author  : vincent
@Time    : 2020/8/28 4:53 下午
@Version : 1.0
'''
import logging
import os

from flask import render_template, request, Flask, jsonify
from werkzeug.routing import BaseConverter

from fund_analysis.tools import utils
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


@app.route('/<regex(".*.html"):url>')
def html_request(url):
    return render_template(url)


@app.route('/execute', methods=['POST'])
def execute():
    request_data = request.get_json()
    logger.debug(request_data)
    command = request_data['command']
    logger.debug("需要运行的命令：%s", command)
    result, base64_images = run(command)
    return jsonify({'result': result, 'images': base64_images})


def run(command):
    """
    fund_analysis.analysis.calculate_alpha --code 009549 --type fund --period week --index 上证指数
    :return:
    """
    module_name = command.split(" ")[0]
    import importlib
    command_module = importlib.import_module(module_name)

    io_stream, original_stdout, original_logger_stdout = start_capture_console()
    base64_images = command_module.main(command.split(" ")[1:])
    result = end_capture_console(io_stream, original_stdout, original_logger_stdout)
    logger.debug("命令：[%s]\n%s", command, result)
    logger.debug("生成图片：[%d]张", len(base64_images))

    return result, base64_images


# python -m fund_analysis.web.server "fund_analysis.analysis.calculate_alpha --code 009549 --type fund --period week --index 上证指数"
# if __name__ == '__main__':
#     run(sys.argv[1])

if __name__ == '__main__':
    utils.init_logger()
    app.run()
