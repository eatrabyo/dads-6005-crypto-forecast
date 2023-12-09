from sqlalchemy import exc, text, bindparam
import pandas as pd

def query_stmt(engine):
    try:
        stmt = """ select * from eth_price;"""
        t = text(stmt)
        df = pd.read_sql(t,con=engine)
        return df
    except exc.SQLAlchemyError as e:
        print(type(e))
        print(e.orig)
        print(e.statement)