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


def get_daily_data(industry='all', fields=['open', 'high', 'low', 'close'], adj=True):
    industrys = get_industrys(level='L1')
    
    if adj:
        adj_fields = ['open', 'high', 'low', 'close']
    else:
        adj_fields = []
    
    data = {}
    
    if industry == 'all':
        industry = list(industrys.keys())

    for field in fields:
        data[field] = DataFrame()
    
    for i in industry:
        for field in fields:
            if field in adj_fields:
                data[field] = pd.concat([data[field], DataFrame({stock: pd.read_csv('../DataBase/StockDailyData/%s/%s.csv'%(i, stock), index_col=[0], parse_dates=[0]).loc[:, field] * pd.read_csv('../DataBase/StockDailyData/%s/%s.csv'%(i, stock), index_col=[0], parse_dates=[0]).loc[:, 'adj_factor'] for stock in industrys[i]})], 1)
            else:
                data[field] = pd.concat([data[field], DataFrame({stock: pd.read_csv('../DataBase/StockDailyData/%s/%s.csv'%(i, stock), index_col=[0], parse_dates=[0]).loc[:, field] for stock in industrys[i]})], 1)

    return data


def centralize(data):
    return data.subtract(data.mean(1), 0)

