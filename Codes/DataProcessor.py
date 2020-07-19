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


def get_stock_money_data(industrys, industry='all', fields=['gt_vol', 'rzye', 'rqye']):
    
    data = {field:DataFrame() for field in fields}
    
    if industry == 'all':
        stocks = [j for i in industrys.values() for j in i]
    else:
        stocks = [j for i in industry for j in industrys[i]]
    
    for stock in stocks:
        if os.path.exists('../DataBase/StockMoneyData/Stock/%s.csv'%stock):
            df = pd.read_csv('../DataBase/StockMoneyData/Stock/%s.csv'%stock, index_col=[0], parse_dates=[0])
            for field in fields:
                data[field].loc[:, stock] = df.loc[:, field]
    
    return data


def get_index_data(industrys, industry='all', fields=['open', 'high', 'low', 'close', 'trf', 'gt_amount', 'rzye', 'rqye', 'buy_sm_amount', 'sell_sm_amount', 'buy_md_amount', 'sell_md_amount', 'buy_lg_amount', 'sell_lg_amount', 'buy_elg_amount', 'sell_elg_amount', 'net_mf_amount',]):
    
    data = {field:DataFrame() for field in fields}
    
    if industry == 'all':
        industry = industrys.keys()
    
    for i in industry:
        df = pd.read_csv('../DataBase/IndexData/Index/%s.csv'%i, index_col=[0], parse_dates=[0])
        for field in fields:
            data[field].loc[:, i] = df.loc[:, field]
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
