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



df3 = pd.DataFrame()
new_data= \
    [["2019-01-10",1.240,1.776,1.97,"!!开放申购","开放赎回", "NaN"],
    ["2019-01-11",1.240,1.776,1.97,"!!开放申购","开放赎回", "NaN"]]
headers=['净值日期','单位净值','累计净值','日增长率','申购状态','赎回状态','分红送配']
new_data = np.array(new_data)
for col, col_name in enumerate(headers):
    print("col,col_name", col, ",", col_name)
    df3[col_name] = new_data[:, col]
df3.set_index("净值日期",inplace=True)
df3.to_csv("test.csv",index="净值日期")



