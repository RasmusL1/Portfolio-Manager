# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 08:59:57 2024

@author: User
"""

import pandas as pd
import requests
import statistics
import numpy as np
import time
import yfinance as yf
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By




def get_yfundamentals(stock_list):
    ### access to yfiancne via selenium webbrowser
    driver = webdriver.Chrome(ChromeDriverManager().install())
    
    driver.get("https://de.finance.yahoo.com/")
    time.sleep(10)
    ### accept cookies
    driver.find_element(By.XPATH, '//button[text()="Alle akzeptieren"]').click()
    time.sleep(2)
    
    ### scrape fundamentals from yahoo and add to stock infos
    data=[]
    for i in range(len(stock_list[3])):   
        #stock_info=[item[i] for item in stock_list]
        
        driver.get("https://de.finance.yahoo.com/quote/"+stock_list[3][i]+"/key-statistics/")
        time.sleep(3)
        html=driver.page_source
        soup=BeautifulSoup(html,'html.parser')
        table_bucket=soup.findAll("td", class_="Pos(st) Start(0) Bgc($lv2BgColor) fi-row:h_Bgc($hoverBgColor) Pend(10px)")
        table_bucket.extend(soup.findAll("td", class_="Pos(st) Start(0) Bgc($lv2BgColor) fi-row:h_Bgc($hoverBgColor) Pend(10px) Miw(140px)"))
        table_bucket.extend(soup.findAll("td", class_="Pos(st) Start(0) Bgc($lv2BgColor) fi-row:h_Bgc($hoverBgColor) Pend(10px) Miw(140px)"))
        
        for y in range(len(table_bucket)):
            if table_bucket[y].text.strip()=="Preis/Buch (mrq)":
                price_book=table_bucket[y].next_sibling.text.strip()
            if table_bucket[y].text.strip()=="Marktkap. (im Tagesverlauf)":
                market_cap=table_bucket[y].next_sibling.text.strip()
            if table_bucket[y].text.strip()=="Erwarteter Jahresdividendenertrag 4":
                dividend_rate=table_bucket[y].next_sibling.text.strip()
            if table_bucket[y].text.strip()=="Erwartetes KGV":
                exp_pe=table_bucket[y].next_sibling.text.strip()
            if table_bucket[y].text.strip()=="Gewinnspanne":
                profit_margin=table_bucket[y].next_sibling.text.strip()
        
        driver.get("https://de.finance.yahoo.com/quote/"+stock_list[3][i]+"/profile/")
        time.sleep(3)
        html=driver.page_source
        soup=BeautifulSoup(html,'html.parser')
        try:
            sector=soup.find('p', class_="D(ib) Va(t)").findAll('span', class_='Fw(600)')[0].text.strip()
        except:
            sector='nan'
                
                
                
        #stats_dict=dict(zip([soup.findAll("td", class_="Pos(st) Start(0) Bgc($lv2BgColor) fi-row:h_Bgc($hoverBgColor) Pend(10px)")[x].text.strip() for x in range(len(soup.findAll("td", class_="Pos(st) Start(0) Bgc($lv2BgColor) fi-row:h_Bgc($hoverBgColor) Pend(10px)")))], [soup.findAll("td",  class_="Fw(500) Ta(end) Pstart(10px) Miw(60px)")[x].text.strip() for x in range(len(soup.findAll("td",  class_="Fw(500) Ta(end) Pstart(10px) Miw(60px)")))]))
        #if not stats_dict:
         #   continue
        
        ### download pricedata
        df = yf.download(stock_list[3][i])
        try:
            df=df[['Open', 'Close']].copy().resample('1D').mean().fillna(method='ffill').iloc[::-1]
        except:
            continue
         ## momentum
        try:
             price_30_days=round((df['Close'].to_list()[0]/df['Close'].to_list()[29])-1,3)
        except:
            price_30_days='NA'
        try:    
            price_90_days=round((df['Close'].to_list()[0]/df['Close'].to_list()[89])-1,3)
        except:
            price_90_days='NA'
        try: 
            price_365_days=round((df['Close'].to_list()[0]/df['Close'].to_list()[364])-1,3)
        except:
            price_365_days='NA'
    
        stock_info={'company': stock_list[0][i],
                    'sector': sector,
                    'wkn': stock_list[1][i],
                    'isin': stock_list[2][i],
                    'ticker': stock_list[3][i],
                    'ask': stock_list[4][i],
                    'bid' : stock_list[5][i],
                    'country': stock_list[6][i],
                    'spread': stock_list[5][i]- stock_list[4][i],
                    'market_cap': market_cap,
                    'price_book': price_book,
                    'dividend_rate': dividend_rate,
                    'forw_pe': exp_pe,
                    'profit_margin': profit_margin,
                    'momentum_30d': price_30_days*100,
                    'momentum_90d': price_90_days*100,
                    'momentum_365d': price_365_days*100
                    }
        print(stock_info)
                    
                    
        #stock_info.extend([market_cap, price_book, dividend_rate, exp_pe, profit_margin, price_30_days, price_90_days, price_365_days])   
        data.append(stock_info)
    driver.quit()
    return data
#print(stats_dict)