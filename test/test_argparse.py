import argparse
parser = argparse.ArgumentParser(description='这是一个xxxx的命令')
parser.add_argument('--code', '-c', type=str, default=None, help="机构代码")
parser.add_argument('--type', '-t', type=str, default=None)  #
parser.add_argument('--index', '-n', type=str)
parser.add_argument('--period', '-p', type=str)

import io

stream = io.StringIO()
print(parser.description)
print("------")
parser.print_usage(stream)
print(stream.getvalue())
print("------")
stream.seek(0)
parser.print_help(stream)

help = stream.getvalue()
help_list = help.split("\n\n")[1:]
for i in help_list:
    print("\t"+i)
stream.close()

# python -m test.test_argparse
