from sqlalchemy import Column, Integer, String, Date, Float, create_engine, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def get_field_values(obj):
    class_name = obj.__class__.__name__

    result = "<" + class_name + "("

    f_names = dir(obj)
    for f_name in f_names:
        if f_name == "metadata": continue
        if f_name == "id": continue
        if f_name.startswith("_"): continue
        result += ",{}={}".format(f_name,getattr(obj, f_name))
    result += ")"
    return result


# 定义映射类Fund，其继承上一步创建的Base
class Fund(Base):
    """
    基金基本信息
    """
    __tablename__ = 'funds'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(100))
    name = Column(String(200))
    start_date = Column(Date())
    end_date = Column(Date())
    fund_type = Column(String(20))  # 基金类别：股票型	货币型	债券型	混合型	基金型	贵金属	封闭式
    advisor = Column(String(20))  # 基金管理人
    trustee = Column(String(20))  # 基金托管人
    operate_mode = Column(String(20))  # 基金运作方式：开放式基金	封闭式基金	QDII	FOF	ETF	LOF
    total_asset = Column(Float())  # 总现值

    __table_args__ = (
        UniqueConstraint('code'),
    )

    # __repr__方法用于输出该类的对象被print()时输出的字符串，如果不想写可以不写
    def __repr__(self):
        return get_field_values(self)


# 定义映射类Fund，其继承上一步创建的Base
class FundStock(Base):
    """
    基金的10大持仓股
    """
    __tablename__ = 'fund_stocks'  # 指定本类映射到users表

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键

    fund_code = Column(String(20))  # 基金编码
    stock_code = Column(String(20))  # 股票编码
    stock_name = Column(String(20))  # 股票名称
    market_cap = Column(String(20))  # 股票市值
    proportion = Column(Float())  # 在基金中的资产占比
    pub_date = Column(Date())  # 披露日期

    __table_args__ = (
        UniqueConstraint('fund_code', 'stock_code'),
    )

    # __repr__方法用于输出该类的对象被print()时输出的字符串，如果不想写可以不写
    def __repr__(self):
        return get_field_values(self)


class StockIndustry(Base):
    """
    股票对应的行业
    """
    __tablename__ = 'stock_industries'

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键
    stock_code = Column(String(20))  # 基金编码
    industry_code = Column(String(20))  # 行业编码
    industry_name = Column(String(20))  # 行业名称

    __table_args__ = (
        UniqueConstraint('stock_code', 'industry_code'),
    )

    # __repr__方法用于输出该类的对象被print()时输出的字符串，如果不想写可以不写
    def __repr__(self):
        return get_field_values(self)

