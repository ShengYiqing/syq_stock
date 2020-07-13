import os
import sys
import time
import datetime
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import tushare as ts

def get_industrys(level='L1'):
    #获取行业分类
    pro = ts.pro_api()
    industrys = {i:pro.index_member(index_code=i).con_code.values for i in pro.index_classify(level=level, src='SW').sort_values('index_code').loc[:, 'index_code']}
    
    return industrys


def get_daily_data(industry='all', fields=['open', 'high', 'low', 'close']):
    industrys = get_industrys(level='L1')
    
    data = {}
    
    if industry == 'all':
        stocks = [j for i in industrys.values() for j in i]
    else:
        stocks = [j for i in industry for j in industrys[i]]
    
    for field in fields:
        data[field] = DataFrame({stock: pd.read_csv('../DataBase/StockDailyData/Stock/%s.csv'%stock, index_col=[0], parse_dates=[0]).loc[:, field] for stock in stocks})
        
    return data


def centralize(data):
    return data.subtract(data.mean(1), 0)

def standardize(data):
    return data.subtract(data.mean(1), 0).divide(data.std(1), 0)

def ma_ratio(data, ma_short, ma_long):
    return data.rolling(ma_short).mean() / data.rolling(ma_long).mean()

def standardize_industry(data):
    industrys = get_industrys(level='L1')
    