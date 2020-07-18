import os
import sys
import time
import datetime
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import tushare as ts

def get_industrys(level='L2'):
    #获取行业分类
    pro = ts.pro_api()
    industrys = {i:pro.index_member(index_code=i).con_code.values for i in pro.index_classify(level=level, src='SW').sort_values('index_code').loc[:, 'index_code']}
    
    return industrys

def get_all_industrys():
    #获取一二级行业分类
    industrys_1 = get_industrys(level='L1')
    industrys_2 = get_industrys(level='L2')
    
    industrys = {}
    industrys.update(industrys_1)
    industrys.update(industrys_2)
    
    return industrys

def get_stock_daily_data(industrys, industry='all', fields=['open',
                                 'high',
                                 'low',
                                 'close',
                                 'adj_factor',
                                 'turnover_rate_f',
                                 'pe_ttm',
                                 'pb',
                                 'ps_ttm',
                                 'total_mv']):
    data = {}
    
    if industry == 'all':
        stocks = [j for i in industrys.values() for j in i]
    else:
        stocks = [j for i in industry for j in industrys[i]]
    
    for field in fields:
        data[field] = DataFrame({stock: pd.read_csv('../DataBase/StockDailyData/Stock/%s.csv'%stock, index_col=[0], parse_dates=[0]).loc[:, field] for stock in stocks})
        
    return data

def get_index_daily_data(industrys, industry='all', fields=['open',
                                 'high',
                                 'low',
                                 'close',
                                 'adj_factor',
                                 'turnover_rate_f',
                                 'pe_ttm',
                                 'pb',
                                 'ps_ttm',
                                 'total_mv']):
    
    if industry == 'all':
        industry = industrys.keys()
        
    data = get_stock_daily_data(industrys, industry, fields)
    
    OPEN = data['open'] * data['adj_factor']
    HIGH = data['high'] * data['adj_factor']
    LOW = data['low'] * data['adj_factor']
    CLOSE = data['close'] * data['adj_factor']
    OPEN.fillna(method='ffill', inplace=True)
    HIGH.fillna(method='ffill', inplace=True)
    LOW.fillna(method='ffill', inplace=True)
    CLOSE.fillna(method='ffill', inplace=True)
    trf = data['turnover_rate_f']

    mv = data['total_mv']

    
    data_industry = {}
    data_industry['open'] = DataFrame({i:OPEN.loc[:, industrys[i]].mean(1) for i in industry})
    data_industry['high'] = DataFrame({i:HIGH.loc[:, industrys[i]].mean(1) for i in industry})
    data_industry['low'] = DataFrame({i:LOW.loc[:, industrys[i]].mean(1) for i in industry})
    data_industry['close'] = DataFrame({i:CLOSE.loc[:, industrys[i]].mean(1) for i in industry})
    
    data_industry['turnover_rate_f'] = DataFrame({i:trf.loc[:, industrys[i]].median(1) for i in industry})
    data_industry['total_mv'] = DataFrame({i:mv.loc[:, industrys[i]].sum(1) for i in industry})
    
    return data_industry

def get_stock_money_data(industrys, industry='all', fields=['gt_vol', 'rzye', 'rqye']):
    
    data = {field:DataFrame() for field in fields}
    
    if industry == 'all':
        stocks = [j for i in industrys.values() for j in i]
    else:
        stocks = [j for i in industry for j in industrys[i]]
    
    for stock in stocks:
        if os.path.exists('../DataBase/StockMoneyData/Stock/%s.csv'%stock):
            df = pd.read_csv('../DataBase/StockMoneyData/Stock/%s.csv'%stock, index_col=[0], parse_dates=[0])
            for field in df.columns:
                data[field].loc[:, stock] = df.loc[:, field]
    
    return data

def centralize(data):
    return data.subtract(data.mean(1), 0)

def standardize(data):
    return data.subtract(data.mean(1), 0).divide(data.std(1), 0)

def ma_ratio(data, ma_short, ma_long):
    return data.rolling(ma_short).mean() / data.rolling(ma_long).mean()

def standardize_industry(data, industrys, industry):
    data_dic = {i:standardize(data.loc[:, industrys[i]]) for i in industry}
    ret = pd.concat([df for df in data_dic.values()], axis=1)
    
    return ret
