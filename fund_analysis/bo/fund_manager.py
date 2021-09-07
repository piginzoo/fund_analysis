from sqlalchemy import Column, Integer, String, UniqueConstraint

from fund_analysis.bo.fund import Base, DBInfoMixin


class FundManager(Base, DBInfoMixin):
    """
    基金经理们
    """

    __tablename__ = 'fund_manager'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(100))
    manager = Column(String(200))
    start = Column(String(100))
    end = Column(String(200))
    period = Column(String(100))
    earn = Column(String(200))

    __table_args__ = (
        UniqueConstraint('code'),
    )

    def get_column_mapping(self):
        return {
            'code': '代码',
            'manager': '基金经理',
            'start': '开始时间',
            'end': '结束时间',
            'period': '任职时间',
            'earn': '任职回报'
        }

    # __repr__方法用于输出该类的对象被print()时输出的字符串，如果不想写可以不写
    def __repr__(self):
        return self.get_field_values()
