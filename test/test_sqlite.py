from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

"""
# 参考：https://www.cnblogs.com/lsdb/p/9835894.html
echo=Ture----echo默认为False，表示不打印执行的SQL语句等较详细的执行信息，改为Ture表示让其打印。
check_same_thread=False----sqlite默认建立的对象只能让建立该对象的线程使用，
而sqlalchemy是多线程的所以我们需要指定check_same_thread=False来让建立的对象任意线程都可使用。
"""

Base = declarative_base()


# 定义映射类Fund，其继承上一步创建的Base
class Fund(Base):
    # 指定本类映射到users表
    __tablename__ = 'funds'
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 指定name映射到name字段; name字段为字符串类形，
    name = Column(String(20))
    age = Column(String(20))

    # __repr__方法用于输出该类的对象被print()时输出的字符串，如果不想写可以不写
    def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % (
            self.name, self.fullname, self.password)


engine = create_engine('sqlite:///data/db/funds.db?check_same_thread=False', echo=True)
Base.metadata.create_all(engine, checkfirst=True)

# engine是2.2中创建的连接
Session = sessionmaker(bind=engine)

# 创建Session类实例
session = Session()

session.add(Fund(name='abc'))

session.commit()

# python -m test.test_sqlite
