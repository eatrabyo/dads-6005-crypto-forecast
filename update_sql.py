from sqlalchemy import text

def insert_eth(df,engine):
    with engine.begin() as conn:
            sql = """
            INSERT INTO eth_price SET datetime = :datetime,
            pct_chg = :priceChangePercent,
            close = :lastPrice,
            open = :openPrice,
            high = :highPrice,
            low = :lowPrice,
            volume = :volume,
            avg_price = :avg_price

            """
            
            params = df.to_dict("records")
            conn.execute(text(sql), params)