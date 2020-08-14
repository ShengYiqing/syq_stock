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

industrys = get_all_industrys()

for industry in industrys.keys():
    stocks = industrys[industry]
    stocks_daily_data = {stock:pd.read_csv('../StockDailyData/Stock/%s.csv'%stock, index_col=[0], parse_dates=[0]) for stock in stocks}
    ADJ_FACTOR = DataFrame({stock:stocks_daily_data[stock].adj_factor for stock in stocks})
    OPEN = DataFrame({stock:stocks_daily_data[stock].open for stock in stocks}).fillna(method='ffill') * ADJ_FACTOR
    HIGH = DataFrame({stock:stocks_daily_data[stock].high for stock in stocks}).fillna(method='ffill') * ADJ_FACTOR
    LOW = DataFrame({stock:stocks_daily_data[stock].low for stock in stocks}).fillna(method='ffill') * ADJ_FACTOR
    CLOSE = DataFrame({stock:stocks_daily_data[stock].close for stock in stocks}).fillna(method='ffill') * ADJ_FACTOR
    AMOUNT = DataFrame({stock:stocks_daily_data[stock].amount for stock in stocks}).fillna(method='ffill') * ADJ_FACTOR * 1000
    VOL = DataFrame({stock:stocks_daily_data[stock].vol for stock in stocks}).fillna(method='ffill') * 100
    VWAP_S = AMOUNT / VOL
    TRF = DataFrame({stock:stocks_daily_data[stock].turnover_rate_f for stock in stocks})
    
    stocks_money_data = {stock:pd.read_csv('../StockMoneyData/Stock/%s.csv'%stock, index_col=[0], parse_dates=[0]) for stock in stocks}
    GT_AMOUNT = DataFrame({stock:stocks_money_data[stock].gt_vol for stock in stocks}) * (OPEN+HIGH+LOW+CLOSE) / 4
    
    RZYE = DataFrame({stock:stocks_money_data[stock].rzye for stock in stocks})
    RQYE = DataFrame({stock:stocks_money_data[stock].rqye for stock in stocks})
    
    buy_sm_amount = DataFrame({stock:stocks_money_data[stock].buy_sm_amount for stock in stocks})
    sell_sm_amount = DataFrame({stock:stocks_money_data[stock].sell_sm_amount for stock in stocks})
    buy_md_amount = DataFrame({stock:stocks_money_data[stock].buy_md_amount for stock in stocks})
    sell_md_amount = DataFrame({stock:stocks_money_data[stock].sell_md_amount for stock in stocks})
    buy_lg_amount = DataFrame({stock:stocks_money_data[stock].buy_lg_amount for stock in stocks})
    sell_lg_amount = DataFrame({stock:stocks_money_data[stock].sell_lg_amount for stock in stocks})
    buy_elg_amount = DataFrame({stock:stocks_money_data[stock].buy_elg_amount for stock in stocks})
    sell_elg_amount = DataFrame({stock:stocks_money_data[stock].sell_elg_amount for stock in stocks})
    net_mf_amount = DataFrame({stock:stocks_money_data[stock].net_mf_amount for stock in stocks})
    
    index = DataFrame({'open':OPEN.mean(1),
                       'high':HIGH.mean(1),
                       'low':LOW.mean(1),
                       'close':CLOSE.mean(1),
                       'vwap':VWAP_S.mean(1),
                       'trf':TRF.median(1),
                       'gt_amount':GT_AMOUNT.sum(1),
                       'rzye':RZYE.sum(1),
                       'rqye':RQYE.sum(1),
                       'buy_sm_amount':buy_sm_amount.sum(1),
                       'sell_sm_amount':sell_sm_amount.sum(1),
                       'buy_md_amount':buy_md_amount.sum(1),
                       'sell_md_amount':sell_md_amount.sum(1),
                       'buy_lg_amount':buy_lg_amount.sum(1),
                       'sell_lg_amount':sell_lg_amount.sum(1),
                       'buy_elg_amount':buy_elg_amount.sum(1),
                       'sell_elg_amount':sell_elg_amount.sum(1),
                       'net_mf_amount':net_mf_amount.sum(1),
            }, index=OPEN.index)
    '''
                       'gt_amount':GT_AMOUNT.sum(1),
                       'rzye'RZYE.sum(1),
                       'rqye'RQYE.sum(1),
                       'buy_sm_amount':buy_sm_amount.sum(1),
                       'sell_sm_amount':sell_sm_amount.sum(1),
                       'buy_md_amount':buy_md_amount.sum(1),
                       'sell_md_amount':sell_md_amount.sum(1),
                       'buy_lg_amount':buy_lg_amount.sum(1),
                       'sell_lg_amount':sell_lg_amount.sum(1),
                       'buy_elg_amount':buy_elg_amount.sum(1),
                       'sell_elg_amount':sell_elg_amount.sum(1),
                       'net_mf_amount':net_mf_amount.sum(1),
                       '''
    index.to_csv('../IndexData/Index/%s.csv'%industry)