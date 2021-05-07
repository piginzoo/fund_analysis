from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
from sqlalchemy import create_engine

from fund_analysis.bo.fund import Fund, FundStock, StockIndustry
from fund_analysis.bo.fund_analysis import FundAnalysis

if __name__ == '__main__':
    # 查看映射对应的表
    FundAnalysis.__table__
    Fund.__table__
    FundStock.__table__
    StockIndustry.__table__

    # 创建数据表。一方面通过engine来连接数据库，另一方面根据哪些类继承了Base来决定创建哪些表
    # checkfirst=True，表示创建表前先检查该表是否存在，如同名表已存在则不再创建。其实默认就是True
    engine = create_engine('sqlite:///data/db/funds.db?check_same_thread=False', echo=True)
    # Base.metadata.drop_all(engine, checkfirst=True)
    Base.metadata.create_all(engine, checkfirst=True)

    print("所有的表已经创建...")
