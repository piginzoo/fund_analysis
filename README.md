# 基金分析项目

这是一个自己使用的分析基金的项目，目前只有一个需求，就是可以分析一个基金的定投情况

懒得架数据库，都用文件存储了

# 定投受益分析

输入一个基金代码，然后获取他的所有数据，如果已经爬过了，就不在爬了，
如果没有，去爬取他的数据，然后以文本的方式保存到db目录，
然后用命令行的方式打印出他的分析结果。

# 爬取思路

如何办证，爬过之后不用再爬，采用pandas的dataframe csv化，
爬取的时候，按照时间爬，每次启动，一定是当前日期，向前爬取3个月，如果爬取过，就不在爬了，
所以爬的参数一定是(now~ now-30)，然后分page，每page 40条，
或者最好的方法是到日期级别的查重，
每次爬的时候，都按照日期去朝赵，是否爬过，
如果已经爬过了，找到最后的一天的爬取内容，然后从那一天开始向后爬40页，

细节参考：<https://github.com/weibycn/fund>

```
基金净值数据
http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code=377240
http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code=160220&page=1
http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code=160220&page=1&per=50
http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code=377240&page=1&per=20&sdate=2017-03-01&edate=2017-03-01
```

```
调用样例：
https://fundf10.eastmoney.com/F10DataApi.aspx?type=lsjz&code=161725&page=1&per=40
2021-04-19
records:1438,pages:36,curpage:1
```

先爬一下最新的日期，可以得到一共有多少天的数据，也就是这个基金的历史，
比如这个数据就是：1438天，
然后我们可以根据我已经爬来的数据，找到最后一天的，然后指定一个爬取计划，
比如我们当前爬取的最后的一天是2020.12.3号，
我们就可以爬取从2020.12.4~2021.4.19号的数据，
然后40条/页去爬取，然后交给dataframe去建立索引，免去我去排序，
然后爬取完之后，可以检验，如果发现中间漏了哪些，
需要用指定日期的方式去爬取，补齐，
从而避免再次爬取的问题。