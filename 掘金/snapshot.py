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

def f(date, stocks):
    if not os.path.exists('D:/stock/DataBase/StockSnapshootData/%s'%date):
            os.mkdir('D:/stock/DataBase/StockSnapshootData/%s'%date)
    for i in stocks.index:
        if stocks.loc[i, 'list_date'] < date:
            stock = 'SZSE.' + stocks.loc[i, 'symbol']
            history_data = history(symbol=stock, frequency='tick', start_time=datetime.datetime.strptime(date, '%Y%m%d'),  end_time=(datetime.datetime.strptime(date, '%Y%m%d')+datetime.timedelta(1)), df=True)
            history_data.to_csv("D:/stock/DataBase/StockSnapshootData/%s/%s.csv"%(date, stock))

# 策略中必须有init方法
def init(context):
    global start_date
    global end_date
    pro = ts.pro_api()
    #获取日期
    df_dates = pro.trade_cal(exchange='SZSE', start_date=start_date, end_date=end_date)
    dates = df_dates.cal_date[df_dates.is_open==1]
    #获取股票
    stocks = pro.stock_basic(fields='symbol, list_date, market')
    stocks = stocks.loc[stocks.market=='创业板', :]
    #取数写入
    #pool = mp.Pool(2)

    for date in dates:
        #pool.apply_async(func=f, args=(date, stocks))

        if not os.path.exists('D:/stock/DataBase/StockSnapshootData/%s'%date):
            os.mkdir('D:/stock/DataBase/StockSnapshootData/%s'%date)
        for i in stocks.index:
            if stocks.loc[i, 'list_date'] < date:
                stock = 'SZSE.' + stocks.loc[i, 'symbol']
                history_data = history(symbol=stock, fields='quotes, created_at, price, last_volume, last_amount, trade_type', frequency='tick', start_time=datetime.datetime.strptime(date, '%Y%m%d'),  end_time=(datetime.datetime.strptime(date, '%Y%m%d')+datetime.timedelta(1)), df=True)

                if len(history_data) == 0:
                    continue
                history_data.loc[:, 'created_at'] = [timestamp.tz_localize(tz=None) for timestamp in history_data.loc[:, 'created_at']]
                history_data = history_data.set_index('created_at')
                
                history_data.loc[:, 'bid_price_1'] = [i[0]['bid_p'] for i in history_data.quotes]
                history_data.loc[:, 'bid_price_2'] = [i[1]['bid_p'] for i in history_data.quotes]
                history_data.loc[:, 'bid_price_3'] = [i[2]['bid_p'] for i in history_data.quotes]
                history_data.loc[:, 'bid_price_4'] = [i[3]['bid_p'] for i in history_data.quotes]
                history_data.loc[:, 'bid_price_5'] = [i[4]['bid_p'] for i in history_data.quotes]
                history_data.loc[:, 'ask_price_1'] = [i[0]['ask_p'] for i in history_data.quotes]
                history_data.loc[:, 'ask_price_2'] = [i[1]['ask_p'] for i in history_data.quotes]
                history_data.loc[:, 'ask_price_3'] = [i[2]['ask_p'] for i in history_data.quotes]
                history_data.loc[:, 'ask_price_4'] = [i[3]['ask_p'] for i in history_data.quotes]
                history_data.loc[:, 'ask_price_5'] = [i[4]['ask_p'] for i in history_data.quotes]
                
                history_data.loc[:, 'bid_vol_1'] = [i[0]['bid_v'] for i in history_data.quotes]
                history_data.loc[:, 'bid_vol_2'] = [i[1]['bid_v'] for i in history_data.quotes]
                history_data.loc[:, 'bid_vol_3'] = [i[2]['bid_v'] for i in history_data.quotes]
                history_data.loc[:, 'bid_vol_4'] = [i[3]['bid_v'] for i in history_data.quotes]
                history_data.loc[:, 'bid_vol_5'] = [i[4]['bid_v'] for i in history_data.quotes]
                history_data.loc[:, 'ask_vol_1'] = [i[0]['ask_v'] for i in history_data.quotes]
                history_data.loc[:, 'ask_vol_2'] = [i[1]['ask_v'] for i in history_data.quotes]
                history_data.loc[:, 'ask_vol_3'] = [i[2]['ask_v'] for i in history_data.quotes]
                history_data.loc[:, 'ask_vol_4'] = [i[3]['ask_v'] for i in history_data.quotes]
                history_data.loc[:, 'ask_vol_5'] = [i[4]['ask_v'] for i in history_data.quotes]
                history_data.drop(labels='quotes', axis=1, inplace=True)

                history_data.to_csv("D:/stock/DataBase/StockSnapshootData/%s/%s.csv"%(date, stock))
                print(date, stock, ' download')
    #pool.close()
    #pool.join()
if __name__ == '__main__':
    print(start_date, end_date)
    run(strategy_id='64018e9a-0554-11eb-81e8-1a259301b6c6',
        filename='snapshot.py',
        mode=MODE_BACKTEST,
        token='005bc7161f87579bc050fb3b0e74f9c94e136974',
        backtest_start_time='2017-06-17 13:00:00',
        backtest_end_time='2017-08-21 15:00:00')
