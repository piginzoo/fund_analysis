from fund_analysis.bo.fund import Fund


def get_fund(code,session):
    fund = session.query(Fund).filter(Fund.code == code).limit(1).first()

