from sqlalchemy import text

def insert_eth(df,engine):
    with engine.begin() as conn:
            sql = """
            INSERT INTO eth_price SET datetime = :closeTime,
            pct_chg = :priceChangePercent,
            close = :lastPrice,
            open = :openPrice,
            high = :highPrice,
            low = :lowPrice,
            volume = :volume,
            w_avg_price = :weightedAvgPrice

            ON DUPLICATE KEY UPDATE
            pct_chg = :priceChangePercent,
            close = :lastPrice,
            open = :openPrice,
            high = :highPrice,
            low = :lowPrice,
            volume = :volume,
            w_avg_price = :weightedAvgPrice
            """
            
            params = df.to_dict("records")
            conn.execute(text(sql), params)