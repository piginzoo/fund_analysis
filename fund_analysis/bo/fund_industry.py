from sqlalchemy import Column, Integer, String, UniqueConstraint

from fund_analysis.bo import get_field_values
from fund_analysis.bo.fund import Base


class FundIndustry(Base):
    """
    基金的分析信息
    """
    __tablename__ = 'fund_industry'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(100))
    name = Column(String(200))
    industry_code = Column(String(100))
    industry_name = Column(String(200))

    __table_args__ = (
        UniqueConstraint('code'),
    )

    # __repr__方法用于输出该类的对象被print()时输出的字符串，如果不想写可以不写
    def __repr__(self):
        return get_field_values(self)