import pandas as pd

df_read_csv2 = pd.read_csv("../db/161725.csv",index_col='净值日期')
df_read_csv2 = df_read_csv2.sort_index()
df_read_csv2.to_csv("../db/161725.csv", index='净值日期')
df_read_csv2.describe()

df_read_csv2 = pd.read_csv("../db/519778.csv",index_col='净值日期')
df_read_csv2 = df_read_csv2.sort_index()
df_read_csv2.to_csv("../db/519778.csv", index='净值日期')
