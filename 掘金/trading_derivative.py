# coding=utf-8
from __future__ import print_function, absolute_import
from gm.api import *
import tushare as ts
import datetime
import time
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import sys
import os
import multiprocessing as mp
import pickle

if len(sys.argv) == 3:
    start_date = sys.argv[1]
    end_date = sys.argv[2]
elif len(sys.argv) == 2:
    start_date = sys.argv[1]
    end_date = sys.argv[1]
elif len(sys.argv) == 1:
    start_date = datetime.datetime.today().strftime('%Y%m%d')
    end_date = datetime.datetime.today().strftime('%Y%m%d')
else:
    print('date?')
    exit()

# 策略中必须有init方法
def init(context):
    
    global start_date
    global end_date
    pro = ts.pro_api()
    #获取股票
    stocks = pro.stock_basic(fields='symbol').iloc[:,0]
    qianzhui = Series(['SZSE.' if (stock[0]=='0' or stock[0]=='3') else 'SHSE.' for stock in stocks], index=stocks.index)
    houzhui = Series(['.SZ' if (stock[0]=='0' or stock[0]=='3') else '.SH' for stock in stocks], index=stocks.index)
    symbols = qianzhui + stocks
    filename = stocks + houzhui

    daily_df = DataFrame()

    for ind in stocks.index:
        data = get_fundamentals(table='trading_derivative_indicator', symbols=symbols.loc[ind], start_date=start_date, end_date=end_date, 
                fields='TCLOSE,NEGOTIABLEMV,TOTMKTCAP,TURNRATE,DY,EV,EVEBITDA,EVPS,LYDY,PB,PCTTM,PETTM,PETTMNPAAEI,PSTTM', df=True)
        if len(data) > 0:
            data.index = [timestamp.strftime('%Y%m%d') for timestamp in data.loc[:, 'end_date']]
            data.drop(labels='pub_date', axis=1, inplace=True)
            data.drop(labels='end_date', axis=1, inplace=True)
            if os.path.exists('D:/stock/DataBase/StockTradingDerivativeData/Stock/%s.csv'%(filename.loc[ind])):
                data.to_csv('D:/stock/DataBase/StockTradingDerivativeData/Stock/%s.csv'%(filename.loc[ind]), header=False, mode='a')
            else:
                data.to_csv('D:/stock/DataBase/StockTradingDerivativeData/Stock/%s.csv'%(filename.loc[ind]))
            daily_df = pd.concat([daily_df, data.iloc[-1:]], axis=0, sort=False)
        print(stocks.loc[ind], 'Downloaded')
    daily_df.to_csv('D:/stock/DataBase/StockTradingDerivativeData/Daily/%s.csv'%(daily_df.index[-1]))

if __name__ == '__main__':
    run(strategy_id='64018e9a-0554-11eb-81e8-1a259301b6c6',
        filename='trading_derivative.py',
        mode=MODE_BACKTEST,
        token='005bc7161f87579bc050fb3b0e74f9c94e136974',
        backtest_start_time='2016-06-17 13:00:00',
        backtest_end_time='2017-08-21 15:00:00')
