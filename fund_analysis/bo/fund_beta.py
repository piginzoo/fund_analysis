from sqlalchemy import Column, Integer, String, Float, UniqueConstraint

from fund_analysis.bo import get_field_values
from fund_analysis.bo.fund import Base


class FundBeta(Base):
    """
    基金的beta值
    """
    __tablename__ = 'fund_beta'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(100))
    name = Column(String(200))
    index_code = Column(String(50)) # 基于的指数代码
    index_name = Column(String(50)) # 基于的指数名称
    beta = Column(Float())

    __table_args__ = (
        UniqueConstraint('code','index_code'),
    )


    # __repr__方法用于输出该类的对象被print()时输出的字符串，如果不想写可以不写
    def __repr__(self):
        return get_field_values(self)
