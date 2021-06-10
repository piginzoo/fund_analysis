#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Title   : 模块
@File    :   __init__.py
@Author  : vincent
@Time    : 2020/8/28 4:53 下午
@Version : 1.0
'''
import json
import logging
import os,sys

from flask import render_template, request, make_response, Flask

from fund_analysis.tools.utils import start_capture_console, end_capture_console

base_path = os.getcwd()
template_path = os.path.join(base_path, "fund_analysis/web/templates")
static_path = os.path.join(base_path, "fund_analysis/web/static")

app = Flask('app',
            template_folder=template_path,
            static_folder=static_path,
            static_url_path="/static")

logger = logging.getLogger(__name__)


@app.route('/', methods=["GET"])
def demo_index():
    return render_template("main.html")


@app.route('/execute', methods=['POST'])
def execute():
    io_stream, original_stdout, original_logger_stdout = start_capture_console()
    username = request.form.get('params', None, str)
    html = end_capture_console(io_stream, original_stdout, original_logger_stdout)
    return make_response(json.dumps(responseJson))

def run(command):
    """
    fund_analysis.analysis.calculate_alpha --code 009549 --type fund --period week --index 上证指数
    :return:
    """
    module_name = command.split(" ")[0]
    print(module_name)
    command_module = __import__(module_name)
    print(command_module)
    command_module.main(command.split(" ")[1:])
    # https://www.zky.name/article/72.html

# python -m fund_analysis.web.server "fund_analysis.analysis.calculate_alpha --code 009549 --type fund --period week --index 上证指数"
if __name__ == '__main__':
    run(sys.argv[1])