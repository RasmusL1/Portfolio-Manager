# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 10:07:49 2024

@author: User
"""


import psycopg2
from psycopg2.extras import Json
from db_config import config
import scrape_finanzen
import scrape_yf



### Get scraped stock-info from finanzen.net
stock_list=scrape_finanzen.get_stockinfo()
print('+++finanzen.net scraped+++')

### add scraped fundamentals from yfinance
data=scrape_yf.get_yfundamentals(stock_list)
print('+++yahoofinance scraped+++')

## connect to sql database
params = config()
conn = psycopg2.connect(**params)
cur = conn.cursor()

### delete old data
cur.execute("DROP TABLE IF EXISTS stocks")
cur.execute('''CREATE TABLE stocks(dict JSONB)''')
conn.commit()

for stock_data in data:
    cur.execute('INSERT into stocks (dict) values (%s)',
              [Json(stock_data)])
    conn.commit()

    
conn.close()