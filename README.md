# 基金分析项目

  * [基金分析项目](#基金分析项目)
    * [概述](#概述)
    * [1.基金数据爬取](#1-基金数据爬取)
    * [2.定投分析](#2-定投分析)
    * [3.定投利润计算](#3-定投利润计算)
    * [4.基金分析](#4-基金分析)
  * [数据一览](#数据一览)   
  * [所有命令一览](#命令一览)
  * [开发日志](#开发日志)
  * [参考](#参考)

## 概述
这是一个自己使用的分析基金的项目，可以对基金进行多种分析，方便自己的投资。

**【主要功能】**

目前主要实现一下features：

- [x] 爬取所有的基金数据（从天天基金网，不过貌似yahoo finance都免费提供）
- [x] 显示基金数据
- [x] 可以计算任意一个基金的定投的收益率（固定周期、固定投资额）
- [x] 可以计算你自己的定投计划的收益率（可以是是非固定周期、非固定投资额） 
- [x] 从JoinQuant上爬取所有的基金的信息（流通股、行业、市值等）
- [x] 计算每个基金的所有的补充信息（夏普指数、风险、等）
- [x] 筛选出对冲行业的、市值大的、夏普指数高的基金
- [x] 爬取股票数据（使用了JQData API）
- [x] 根据CAPM，计算每个基金的beta系数
- [x] 根据Jensen Alpha，计算每个基金的alpha系数和Beta系数
- [x] 计算每个基金的alpha系数
- [x] 计算这些备选基金的有效前沿（参考柴知道的CAPM计算方法）
- [x] 做计量假设检验，根据数据做假设检验，判断结论正确性
- [x] 实现一个简易的Web交互界面
- [x] 实现基金评价模型：Treynor-Mazuy四因子模型
- [ ] 实现HM、C-L模型
- [ ] 实现一个使用的选基的策略
- [ ] 尝试使用Fama-French的三因子模型分析基金
- [ ] 实现一个比较容易的回测框架


**【基金数据】**

目前，所有基金数据爬取后，会以csv文本文件方式，保存在data/db目录下。如果你不想从头爬取，可以参阅[爬取结果](#爬取结果)中提供的百度云盘链接，
下载截止到2021.4.21日的基金数据，解压缩到data/db目录下，然后断点续爬最新的数据，可以节省时间。
所有的基金列表，在[fund_list.db](data/db/fund_list.db)中。

\* *采用了简易的sqlite，数据量不大，使用这类嵌入数据库，以求不依赖环境*

**【运行程序】**

可以参考[命令一览](#命令一览)，来了解如何运行这些功能。

**【其他】**

此repo有一个关联项目:[基金分析](https://github.com/users/piginzoo/projects/1)，这个项目是github项目，里面提供了需求看板，方便需求更新。

另外，还创建了一个gitbook：[我的金融工具箱](https://finbook.piginzoo.com/)，用来编写我对金融知识的积累。

## 1 基金数据爬取

### 1.1 爬取基金日净值数据

从[天天基金](https://fund.eastmoney.com/)爬取基金的净值数据，可以单独爬取一只，
也可以爬取所有的基金；并且支持断点续爬。

**【如何运行】**

运行爬虫，只需要运行crawler.sh即可：

```
    bin/crawler.sh
```
运行这个命令，即可运行爬虫，目前有一下运行选项：
- bin/crawler.sh all 爬取所有的基金，支持增量爬取，即可以继续爬取自上次爬取后最新的数据
- bin/crawler.sh --code xxxxx 指定爬取一只基金，xxxxx为基金代码


**【实现思路】**

先实现单个基金的爬取，使用request包，拼出来爬取的url，
然后对返回的结果进行解析，形成pandas的DateFrame，
最终利用dataframe的to_csv，保存到 data/db文件夹，
数据文件的命名方式为 <code>.csv。

CSV文件格式：
第一行是表头：

[净值日期,单位净值,累计净值,日增长率,申购状态,赎回状态,分红送配]

样例数据：

| 净值日期 | NO  | 单位净值 | 累计净值 | 日增长率 | 申购状态 | 赎回状态 | 分红送配 |
|:-------|:----|:--------|:--------|:-------|:--------|:-------|:--------|
|2008-05-19|35|1.442|3.123|-0.07|开放申购|开放赎回|
|2008-05-20|34|1.4  |3.081|-2.91|开放申购|开放赎回|
|2008-05-21|33|1.416|3.098|1.21 |开放申购|开放赎回|
|2008-05-22|32|1.406|3.088|-0.71|开放申购|开放赎回|



**【细节问题】**
- 如何保存数据？
  没有用数据库，而是采用了最直白的文本csv文件，用dataframe.to_csv，形成csv文件。
- 如何保证爬取后，不再爬取？
  每次爬取，都从dataframe的数据文件中，找到最后的一次爬取日期，然后从当日到这个最后一次爬取日期之间的数据，都进行爬取。
- 如何实现增量爬取
  上面已经解释过，会只爬取最后的日期到今天的数据了，所以增量爬取应该很快
- 爬取参数有哪些？
  爬取参数，包含了每页爬几条（目前是40条），爬取第几页，日期是从什么时候到什么时候   
- 日期排序
  爬取完一页是不保存的，而是等都爬取完，才保存，保存之前，会按照日期排序，日期是index，方便检索和排序
- 爬取频率
  为了防止被封，目前的爬取频次是0~1秒之间的间歇，而且是一个进程
  
这个项目，主要参考了：<https://github.com/weibycn/fund>

使用到的web数据接口是[天天基金](https://fund.eastmoney.com/)的api：
```
http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code=377240&page=1&per=20&sdate=2017-03-01&edate=2017-03-01
```

**【爬取结果】**

按照0~1的间隔持续爬取了40个小时，终于爬下来所有的数据，大概是11000个基金，300M的大小，压缩后是55M，由于太大，我没有放到git中，
而是放到百度云盘上。下载后，请解压缩数据到 <data/db> 文件夹中：

链接: < https://pan.baidu.com/s/19m7vbKTYhICRob7pKilydw> 提取码: **bdff** 

### 1.2 爬取基金基本数据

上述是爬取天天基金网的净值日数据，但是，我们还需要基金的其他信息，如：
- 基金的当前市值（用它可以筛选掉小市值基金）
- 基金公司的信息
- 基金的行业信息

因此，我们还需要另外一个爬虫来获得这些信息，幸运的是，我们找到了[JoinQuant](https://www.joinquant.com/help/api/)，
他们免费提供基金的信息，而且是以python API的方式，非常方便，我简单封装了一个他的API，
然后跑下来所有的基金信息，保存到了数据库中。

注意！前面的爬取结果是直接保存到了csv文件中，而这些新的爬取信息，我改存到数据库中，
我是用的是sqlite，原因是，它是python3中默认自带的数据库引擎，也就是说，你不需要
安装任何软件，就可以创建、访问和操作sqlite数据库，很方便、很轻量级。
配合sqlalchemy的ORM数据库API，很方便使用，我后续的各种数据库都使用sqlite了。

## 2 定投分析

可以跑一下一个基金，在某个时期内，按照某种频次定投的收益率是多少。

如何运行：

```
bin/invest.sh --code <基金代码> --start <定投开始日期> --end <定投结束日期> --period <day|week|month> --day <第几日>"
```

需要输入一下参数：
 - code     基金代码
 - start    定投开始日期 
 - end      定投结束日期
 - period <day|week|month>，分别代表是每天都定投、每周都定投、每个月都定投 
 - day      第几日，意思是每周第几天、每个月第几天，当period为day时候此参数无效 

样例：

```
bin/invest.sh --code 519778 --start 2020-01-01 --end 2021-04-22 --period week --day 1

INFO : 加载了[data/db/519778.csv]数据，行数：748
DEBUG : 数据经过[week]过滤,剩余64条
DEBUG : 最后一天[2021-04-20]的价格为：3.20
INFO : 代码[519778] 按[周]定投 64 次, [2020-01-01] -> [2021-04-22] 定投收益率: 121.328%, 耗时: 0.09
```

## 3 定投利润计算 

用来计算真实的投机计划的利润情况，你可以把你自己的真实投资记录导入到一个文本格式中（格式下面会讲），然后跑一遍利润计算。
你可能会问，基金公司都已经替我计算过了，你为何又要计算一遍，原因是，我们可以更透明地理解基金公司是如何管理和计算你的投资和收益的。

### 编写定投文件

你需要编撰一个投资计划文件，文本格式的，格式如下：
`<date>,<amount>`

其中，date是yyyy-mm-dd格式的，必须是这样哈，别的不支持。
如果是定投的话，可以用一下格式表示：
- month_xx，每月第xx日定投，如果遭遇周末或节假日，向后顺延
- week_xx，每周第xx日定投，如果遭遇周末或节假日，向后顺延

下面是一个例子：

```
2020-1-7,5000
2020-1-13,500
2020-2-11,500
2020-2-24,-3231.14 #<-- 赎回
2020-3-2,3300
month_11,1000 #<-- 此后每个月投1000元
```

### 运行利润计算

```
bin/profit.sh --code <基金代码> --plan <定投计划文件>
```

需要输入一下参数：
 - code    基金代码
 - plan    定投计划文件的全路径 
 
样例：

```
bin/profit.sh --code 001938 --plan data/plan/jq_001938.txt

INFO :
基金代码:	 001938 ,
投资计划获利:	22.6489% ，
总投资金额:	20068.86 ,
总账面资产价值:	24614.23 ，
合计获利金额:	4545.37 ，
合计投资天数:	19 天
```

### 利润公式

基金公司在计算利润的时候，刻意夸大了你的利润收益率，她们会将手续费也算在你资产上，而其实是不应该的。

基金公司的利润计算公式 = （基金市值 + 赎回资金 + 手续费） / 扣除手续费的投资额  -  1

而，实际的利润计算公式 = （基金市值 + 赎回资金 ） / 真正的投入资金  -  1

举个例子：

```
    基金公司给出的数据：
    ----------------
    资产价值：54113.71
    基金收益：15.11%
    基金分数：16717.24份

    我计算出来的数据：
    ----------------
    基金代码: 519778 ,
    基金利润: 15.354%, <--- 基本上和他的一致，就是上述的"基金公司的利润计算公式"的结果
    实际利润: 11.896%, <--- 这个才是你真正的收益，其实还要少，因为没有扣除赎回所有的手续费
    投资金额: 82000.000 元,
    手续费  : 1416.879 元,
    实投金额: 80583.121 元,
    总份额  : 16741.296 份,<--- 总份额与基金公司给出的相差24份，可接受
    资产价值: 54191.574 元,
    获利金额: 11171.203 元，
    投资次数: 24 次
```

当然，还是有一些误差，原因如下：

 - 可能是交易日确认的问题，基金公司给出的交易日是他们确认资金的日子，比如你3.18购买了，他3.19号才确认，显示给你的是确认日期，但是实际上，她们是按照你购买日期的价格记录这笔钱的
 - 购买手续费是所谓的**申购手续费**，一般是1.5%，但是实际上的手续费会比这个稍微少个块八毛，不知道为何，比如15元，她们会收14.33之类的诡异数
 - 赎回手续费，是按照期限来的，一般半年内是0.5%，如果超过半年持有，貌似还可以便宜一些，具体得看基金的信息披露

 当然，这个误差可以忽略，时间越久，投资额越大，误差越小，我们计算这个的目的也是为了，让我们的钱投资的明明白白，这个目的基本上达到了。

 所以，可以看到，基金公司不会告诉你究竟手续费是多少，而且，会刻意的夸大你实际可以得到的收益率的。

## 4 基金分析

我对基金进行了指标分析，主要的依据是[夏普指数](https://baike.baidu.com/item/%E5%A4%8F%E6%99%AE%E6%AF%94%E7%8E%87/2549763?fr=aladdin)，
即用 **（收益率-基准利率）/ 标准差**， 我分别计算了年度、季度、月、周的夏普指数，利率我使用的是[中国一年期国债](https://cn.investing.com/rates-bonds/china-1-year-bond-yield)
的利率数据，我下载下来存放到了[bond_interest_CN1YR.db](data/db/bond_interest_CN1YR.db)中，它的利率每天都在变化，都是预估年化的利率值。

具体分析方法：
* 1、仅筛去市值大于10亿，且，类型**混合型、股票型**的基金
* 2、分别按照年、季、月、周，得到每个期间的开始日期和结束日期，例如，得到2020年3月的数据为：[2020.3.1,2020.3.31]
* 3、使用这个日期区间，反向筛选基金日净值数据，仅需要得到期间的开始日期的净值，和结束的净值，用其计算期间的收益率
* 4、使用这个日期区间，反向国债的利率数据
* 5、按照夏普比例公式，计算其夏普指数（分别计算年、季、月、周的，4个数），注意，基准利率要除以期间对应数，比如月，需要除以12
* 6、查询基金的行业归属（取持股最多的股票的行业作为基金的行业属性）
* 7、将结果保存到数据库表[fund_analysis]中

运行完后，可以通过sqlite的客户端，查询行业top10的基金，目前没有写程序，这里先提供SQL方便查询：

```
SELECT code,name,sharpe_quarter,industry_code,industry_name
FROM fund_analysis AS fa1
WHERE code in 
(
      SELECT   code
      FROM     fund_analysis as fa2
      WHERE    fa2.industry_code = fa1.industry_code
      ORDER BY fa2.sharpe_quarter desc
      limit  10
)
ORDER BY industry_code, sharpe_quarter desc
```

# 数据一览

目前数据越来越多，单独在这里列出所有的数据，数据都在 [data] 目录下：
- [funds](data/funds): 以csv文件形式，存放了10000+的基金日净值数据，可以在[百度云盘:提取码bdff](https://pan.baidu.com/s/19m7vbKTYhICRob7pKilydw)下载。
- [plan](data/plan):存放你自己的投资计划，然后就可以帮助计算这个投资计划的收益率
- [bond_interest_CN1YR.db](data/db/bond_interest_CN1YR.db):一年期国债的利率数据
- [fund_list.db](data/db/fund_list.db):存放着所有的基金列表，但是只有很简洁的信息，本质上就是一个csv文本文件
- [industries.db](data/db/industries.db):存放着所有的行业列表，就是一个csv文本文件，目前没有使用
- [funds.db](data/db/funds.db):这是sqilite的数据文件，保存在各类关系数据
- [index](data/index):存放着上证、中证500、沪深300、创业板等多个指数数据

*注：由于数据文件比较大，没有放到git中，可以去[百度云盘:提取码bdff](https://pan.baidu.com/s/19m7vbKTYhICRob7pKilydw)下载相关数据，解压缩到[data]目录下*

# 命令一览

列出了所有的命令行命令，可以通过在根目录下，运行 bin/xxx.sh，来启动以下的各条命令，完成各种功能。
所有命令，都可以通过不带任何参数地运行命令，获得帮助信息。
所有的参数格式都是 --[option] [argment]的格式。

- crawler.sh: 用于爬取天天基金网的某只或所有基金数据
- invest.sh: 用于计算某只基金的定投收益
- profit.sh: 用于计算你自己的某只基金的投资收益，需要你编写一个[投资计划](#编写定投文件)
- show.sh: 用于图像化展示某只基金的数据 
- create_db.sh: 初始化化的数据库表
- analysis.sh: 用来分析夏普指数等信息

# 开发日志

## 2021.6.25
- 完善了一只基金的统计数据的指标，加入了更多的指标，如总收益、年化、最大回撤等
- 实现了一个基于vuejs的简单的展示界面，而且统一了console和web的展示，代码一套，显示2套
- 实现了TM模型的计算
- 跑了一个明星基金经理的基金的TM和各种基本信息的比较的计算

## 2021.6.10
- 完成无风险利率，国债的数据采集
- 完成了股票数据的爬取，接住了JQData的API
- 完成了beta和alpha的计算

## 2021.5.7
- 完成了基金的其他数据的爬取，使用jqdata api
- 完成了夏普和行业分析的代码，并且保存到了sqlite中

## 2021.5.1
增加了图形化显示基金数据的功能

## 2021.4.28
- 实现投资计划的解析
- 实现了真实投资计划利润计算
- 将日期表示都改为datetime，之前为str
- 修正了断掉续爬中的bug

## 2021.4.25
修复了月度的时候定投日是节假日，无法顺延的bug

## 2021.4.23
实现了一个定投的利润率计算，可以跑一个基金从某日到某日的投资收益率。

## 2021.4.21
实现了所有的基金的爬取，基金的列表是取自：<http://fund.eastmoney.com/js/fundcode_search.js>

格式：

```
["000001","HXCZ","华夏成长","混合型","HUAXIACHENGZHANG"]
```
然后不再每次爬取都保存，而是整体一个基金爬取完，才保存。
另外，支持断点续传，如果爬取过的，就不在爬取。
具体实现是，获取爬取的最后的日期，做起起点，一直爬取到昨天（今天的数据没有）
未来可以用这个机制，实现自动的全体的增量爬取。

解决了排序问题，原来是set_index(inplace=True)，要替掉默认的索引。

## 2021.4.20
实现了一个基金的爬取，可以爬取成功了，
也实现了从开始日到节结束日的爬取，
他们的api支持sdate~edate，就是支持日期段爬取的。
并且从中解析出剩余页数，用于循环用。

# 参考
- [基中宝](http://www.glpomelo.cn/index.html),一个做基金推荐的商业网站
