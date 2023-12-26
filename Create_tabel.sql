CREATE TABLE classicmodels.eth_price (
    id INT AUTO_INCREMENT PRIMARY KEY,
    datetime DATETIME,
    open DECIMAL(10, 2),
    high DECIMAL(10, 1),
    low DECIMAL(10, 1),
    close DECIMAL(10, 2),
    volume DECIMAL(10, 4),
    pct_chg DECIMAL(10, 3),
    w_avg_price DECIMAL(30, 8)
);
