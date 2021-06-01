import numpy as np
import pandas as pd

list_l = [[11, 12, 13, 14, 15], [21, 22, 23, 24, 25], [31, 32, 33, 34, 35]]
date_range = pd.date_range(start="20180701", periods=3)
df = pd.DataFrame(list_l, index=date_range,columns=['a', 'b', 'c', 'd', 'e'])
print(df)
df.to_csv("test.csv")
read_csv = pd.read_csv("tzzs_data.csv")
print(read_csv)
df.to_csv("test.csv", index_label="index_label")
df_read_csv2 = pd.read_csv("tzzs_data2.csv")
print(df_read_csv2)

import py


df3 = pd.DataFrame()
new_data= \
    [["2019-01-10", 1.0,1.0,1.97,"!!开放申购","开放赎回", "NaN"],
     ["2019-01-11", 1.240,1.776,1.97,"!!开放申购","开放赎回", "NaN"],
     ["2019-01-12", 1.240, 1.776, 1.97, "!!开放申购", "开放赎回", "NaN"],
     ["2019-01-13", 1.240, 1.776, 1.97, "!!开放申购", "开放赎回", "NaN"],
     ["2019-01-14", 1.240, 1.776, 1.97, "!!开放申购", "开放赎回", "NaN"],
     ["2019-01-15", 1.240, 1.776, 1.97, "!!开放申购", "开放赎回", "NaN"]]

headers=['净值日期','单位净值','累计净值','日增长率','申购状态','赎回状态','分红送配']
new_data = np.array(new_data)
for col, col_name in enumerate(headers):
    print("col,col_name", col, ",", col_name)
    df3[col_name] = new_data[:, col]
df3.set_index("净值日期",inplace=True)
df3.to_csv("test.csv",index="净值日期")

## 日期不对齐，也可以按照index相减，酷
d1= [["2019-01-1", 1],
     ["2019-01-2", 1],
     ["2019-01-3", 1]]
d2= [["2019-01-4", 100],
     ["2019-01-2", 100],
     ["2019-01-1", 100]]
df1 = pd.DataFrame(d1,columns=['date','data1'])
df1.set_index('date',inplace=True)
df2 = pd.DataFrame(d2,columns=['date','data2'])
df2.set_index('date',inplace=True)
df = (df1.iloc[:,0]-df2.iloc[:,0])
print("----------")
df = df.dropna()
print(df)
print(type(df))





