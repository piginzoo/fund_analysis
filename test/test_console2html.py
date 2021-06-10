import io
import logging
import os
import pathlib
import subprocess
import sys

import ansi2html
from ansi2html import Ansi2HTMLConverter
from django.http import HttpResponse
from django.middleware import common
from django.utils.safestring import mark_safe

from fund_analysis.tools import utils

"""
https://vimsky.com/examples/detail/python-method-ansi2html.Ansi2HTMLConverter.html
"""

logger = logging.getLogger(__name__)


def convert_file_contents_to_html2(normalized_output_file):
    # conv = Ansi2HTMLConverter()
    with open(normalized_output_file, "rb") as scan_file:
        test_data = "".join(read_to_unicode(scan_file))
        # expected_data = [e.rstrip('\n') for e in read_to_unicode(scan_file)]
        html = Ansi2HTMLConverter().convert(test_data, ensure_trailing_newline=True)
    return html


# 需要导入模块: import ansi2html [as 别名]
# 或者: from ansi2html import Ansi2HTMLConverter [as 别名]
def ansi2html(s):
    return mark_safe(Ansi2HTMLConverter(inline=True).convert(s, full=False))


def ansi_to_html(ansi_text):
    return Ansi2HTMLConverter(inline=True).convert(wrangle_to_unicode(ansi_text), full=False)


def gen_ansi_output():
    conv = Ansi2HTMLConverter()

    input_file = EXAMPLES_DIR / 'devtools_main.py'
    os.environ['PY_DEVTOOLS_HIGHLIGHT'] = 'true'
    p = subprocess.run((sys.executable, str(input_file)), stdout=subprocess.PIPE, check=True, encoding='utf8')
    html = conv.convert(p.stdout, full=False).strip('\r\n')
    full_html = f'<div class="terminal">\n<pre class="terminal-content">\n{html}\n</pre>\n</div>'
    path = TMP_EXAMPLES_DIR / f'{input_file.stem}.html'
    path.write_text(full_html)
    print(f'generated ansi output to {path}')


def terminalize_output(output):
    # Replace "<,&,>" signs
    output = output.replace("&", "&amp;")
    output = output.replace("<", "&lt;")
    output = output.replace(">", "&gt;")
    output = output.replace("\n", "<br/>")
    '''
       Substitute terminal color codes for CSS tags.
       The bold tag can be a modifier on another tag
       and thus sometimes doesn't have its own
       closing tag. Just ignore it in that case.
    '''
    conv = ansi2html.Ansi2HTMLConverter(escaped=False, scheme="xterm")
    return conv.convert(output, full=False)


def get(self, request, *args, **kwargs):
    filename = self.request.query_params.get('std', None)
    is_html = self.request.query_params.get('html', False)
    if not filename:
        return common.message(500, 'stdout not found')

    options = dbutils.get_stateless_options()
    wss = options.get('WORKSPACES')

    filename = utils.clean_path(filename).strip('/')
    p = pathlib.Path(filename)

    # we don't want a LFI here even when we're admin
    if p.parts[0] not in os.listdir(wss):
        return common.message(500, 'Workspace not found ')

    stdout = utils.join_path(wss, filename)
    content = utils.just_read(stdout)
    if not content:
        return HttpResponse("No result found")

    if filename.endswith('.html') or is_html:
        return HttpResponse(content)

    try:
        # convert console output to html
        conv = Ansi2HTMLConverter(scheme='mint-terminal')
        html = conv.convert(content)
        return HttpResponse(html)
        # return Response(html)
    except:
        return HttpResponse(content)


def format_log(log):
    conv = Ansi2HTMLConverter(dark_bg=False, scheme="solarized", markup_lines=True)
    headers = conv.produce_headers()
    content = conv.convert(log, full=False)
    content = '<pre class="ansi2html-content">{}</pre>'.format(content)
    return headers + content


def do_test_run():
    print("123")
    logger.debug("哈哈哈：%r",12123123)
    import numpy as np
    a = np.random.randint((3,3))
    logger.debug(a)



def do_output():
    import sys

    logger = logging.getLogger()
    original_stdout = sys.stdout  # 保存标准输出流
    original_logger_stdout = logger.handlers[0].stream

    io_stream = io.StringIO("")
    sys.stdout = io_stream
    logger.handlers[0].stream = io_stream

    do_test_run()

    html = io_stream.getvalue()
    full_html = f'<div class="terminal">\n<pre class="terminal-content">\n{html}\n</pre>\n</div>'

    logger.handlers[0].stream = original_logger_stdout
    sys.stdout = original_stdout
    io_stream.close()
    return full_html


if __name__ == '__main__':
    utils.init_logger()
    do_output()