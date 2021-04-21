import os
import pandas as pd

"""
把db目录下的所有数据文件排一次序
"""

files = os.listdir("db")
for f in files:

    if os.path.splitext(f)[-1]!=".csv": continue
    print("重新整理csv文件：",f)
    f_name = os.path.join("db",f)
    df = pd.read_csv(f_name, index_col='净值日期')
    df = df.sort_index()
    df.to_csv(f_name, index='净值日期')

# python -m fund_analysis.sort