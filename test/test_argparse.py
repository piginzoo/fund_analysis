import argparse
parser = argparse.ArgumentParser(description='这是一个xxxx的命令')
parser.add_argument('--code', '-c', type=str, default=None, help="机构代码")
parser.add_argument('--type', '-t', type=str, default=None)  #
parser.add_argument('--index', '-n', type=str)
parser.add_argument('--period', '-p', type=str)

print(parser.description)
print(parser.print_usage())
print(parser.print_help())
