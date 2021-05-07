from sqlalchemy import Column, Integer, String, Date, Float, create_engine, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

from fund_analysis.bo import fund

Base = declarative_base()


class FundAnalysis(Base):
    """
    基金的分析信息
    """
    __tablename__ = 'fund_analysis'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(100))
    name = Column(String(200))
    sharpe_year = Column(Float())
    sharpe_quarter = Column(Float())
    sharpe_month = Column(Float())
    sharpe_week = Column(Float())
    industry_code = Column(String(100))
    industry_name = Column(String(200))

    __table_args__ = (
        UniqueConstraint('code'),
    )

    # __repr__方法用于输出该类的对象被print()时输出的字符串，如果不想写可以不写
    def __repr__(self):
        return fund.get_field_values(self)