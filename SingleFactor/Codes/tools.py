import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
import datetime
import time
import DataProcessor as DP
from scipy.stats import rankdata
import tushare as ts


def get_industrys(level='L1', stocks=None):
    #获取行业分类
    pro = ts.pro_api()
    if stocks:
        def cond(stock):
            return stock in stocks
        industrys = {i:list(filter(cond, pro.index_member(index_code=i).con_code)) for i in pro.index_classify(level=level, src='SW').sort_values('index_code').loc[:, 'index_code']}
    else:
        industrys = {i:list(pro.index_member(index_code=i).con_code) for i in pro.index_classify(level=level, src='SW').sort_values('index_code').loc[:, 'index_code']}
    
    return industrys


def get_stocks(cond=None):
    if cond == None:
        def cond(stock):
            return stock[0] == '3'
    pro = ts.pro_api()
    stocks = pro.stock_basic(fields='symbol').iloc[:,0]
    stocks = [stock + '.SZ' if (stock[0]=='0' or stock[0]=='3') else stock + '.SH' for stock in stocks]
    return list(filter(cond, stocks))


def get_stock_daily_data(stocks=None, industrys=None, industry=None, fields=['open',
                                 'high',
                                 'low',
                                 'close',
                                 'vol',
                                 'amount',
                                 'adj_factor']):
    data = {}
        
    if not stocks:
        if industry == 'all':
            stocks = [j for i in industrys.values() for j in i]
        else:
            stocks = [j for i in industry for j in industrys[i]]
    
    for field in fields:
        data[field] = DataFrame({stock: pd.read_csv('../DataBase/StockDailyData/Stock/%s.csv'%stock, index_col=[0], parse_dates=[0]).loc[:, field] for stock in stocks})
        
    return data


def group_backtest(factor, r, n):
    l = [(((factor.ge(factor.quantile(i/n, 1), 0)) & (factor.le(factor.quantile(i/n+1/n, 1), 0))) * n * r).mean(1).cumsum().rename('%s'%(i/n)) for i in range(n)]
    for i in l:
        (i - r.mean(1).cumsum()).plot()
    plt.legend(['alpha %s'%i.name for i in l])
    '''for i in l:
        i.plot()
    for i in l:
        (i - r.mean(1).cumsum()).plot()
    r.mean(1).cumsum().plot()
    plt.legend([i.name for i in l]+['alpha %s'%i.name for i in l]+['benchmark'])'''
    '''
    for i in range(n):
        q = i / n
        position = (factor.gt(factor.quantile(q, 1), 0)) & (factor.lt(factor.quantile(q+1/n, 1), 0))
        r_backtest = position * r
        daily_r_backtest = r_backtest.mean(1)
        daily_cumsum_r_backtest = daily_r_backtest.cumsum()
    '''
    
    return


def icir(factor, r, n=20, rank=False):
    if rank:
        x1 = DP.standardize(rankdata(factor))
    else:
        x1 = DP.standardize(factor)
    x2 = DP.standardize(r)
    ic = (x1 * x2).mean(1).fillna(0)
    ir = ic.rolling(20).mean() / ic.rolling(20).std()
    
    return ic, ir


def sharpe_ratio_ts(df, n):
    return df.rolling(n).mean() / df.rolling(n).std()


def reg_ts(df, n):
    x = np.arange(n)
    x = x - x.mean()
    b = df.rolling(n).apply(lambda y:(y*x).sum() / (x*x).sum(), raw=True)
    a = df.rolling(n).mean()
    y_hat = a + b * x[-1]
    e = df - y_hat
    
    return b, e


def normalize(df):
    return df.subtract(df.min(1), 0).divide(df.max(1) - df.min(1), 0)

def centralize(data):
    return data.subtract(data.mean(1), 0)

def standardize(data):
    return data.subtract(data.mean(1), 0).divide(data.std(1), 0)

def ma_ratio(data, ma_short, ma_long):
    return data.rolling(ma_short).mean() / data.rolling(ma_long).mean()

def normalize_industry(df, industrys, industry):
    data_dic = {i:normalize(data.loc[:, industrys[i]]) for i in industry}
    ret = pd.concat([df for df in data_dic.values()], axis=1)
    
    return ret

def standardize_industry(data, industrys):
    data_dic = {k:standardize(data.loc[:, industrys[k]]) for k in industrys.keys()}
    ret = pd.concat([df for df in data_dic.values()], axis=1)
    
    return ret

def truncate_outliers(df, percent=0.05):
    tmp = df.copy()
    tmp[tmp.le(tmp.quantile(percent, 1), 0) | tmp.ge(tmp.quantile(1-percent, 1), 0)] = 0
    
    return tmp