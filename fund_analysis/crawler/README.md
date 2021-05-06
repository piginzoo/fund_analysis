目前有2个爬虫：
- 一个是从[天天基金](http://fund.eastmoney.com/)，爬每天的交易信息，
- 一个是从[JoinQuant](https://www.joinquant.com/help/api/)，爬取基金的额外信息

天天基金是纯爬虫，爬取下来每天都报价和收益率，保存到<data/funds>目录中，
以csv格式保存下来，后续可以直接通过DataFrame加载。


而JoinQuant是免费的API，真心不错。用JoinQuant主要为了爬取基金的总市值，
以及持仓信息，这样可以推测出此基金的重仓行业，主要是为了区分行业。
数据存放到了sqlite中，python3是默认带sqlite，很轻量级，很好用。

爬虫的入口是 main.py，可以单独爬一只基金，也可以全面爬取，如果已经爬取的，会忽略。