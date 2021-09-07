from sqlalchemy import Column, Integer, String, Float, UniqueConstraint

from fund_analysis.bo.fund import Base, DBInfoMixin


class FundSharpe(Base,DBInfoMixin):
    """
    基金的分析信息
    """
    __tablename__ = 'fund_sharpe'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(100))
    name = Column(String(200))
    sharpe_year = Column(Float())
    sharpe_quarter = Column(Float())
    sharpe_month = Column(Float())
    sharpe_week = Column(Float())

    __table_args__ = (
        UniqueConstraint('code'),
    )

    def get_column_mapping(self):
        return {
            'code': '代码',
            'name': '名字',
            'sharpe_year': '夏普指数-年',
            'sharpe_quarter': '夏普指数-季',
            'sharpe_month': '夏普指数-月',
            'sharpe_week': '夏普指数-周'
        }


    # __repr__方法用于输出该类的对象被print()时输出的字符串，如果不想写可以不写
    def __repr__(self):
        return self.get_field_values(self)
