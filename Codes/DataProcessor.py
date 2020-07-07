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


def get_daily_data(industry:str, fields:list, adj=True):
    industrys = get_industrys(level='L1')
    
    if adj:
        adj_fields = ['open', 'high', 'low', 'close']
    else:
        adj_fields = []
    
    data = {}
    
    for field in fields:
        if field in adj_fields:
            data[field] = DataFrame({stock: pd.read_csv('../DataBase/StockDailyData/%s/%s.csv'%(industry, stock), index_col=[0], parse_dates=[0]).loc[:, field] * pd.read_csv('../DataBase/StockDailyData/%s/%s.csv'%(industry, stock), index_col=[0], parse_dates=[0]).loc[:, 'adj_factor'] for stock in industrys[industry]})
        else:
            data[field] = DataFrame({stock: pd.read_csv('../DataBase/StockDailyData/%s/%s.csv'%(industry, stock), index_col=[0], parse_dates=[0]).loc[:, field] for stock in industrys[industry]})
    
    return data


def centralize(data):
    return data.subtract(data.mean(1), 0)


