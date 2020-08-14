import tushare as ts
import os
import sys
import time
import datetime
import numpy as np
import pandas as pd
from pandas import Series, DataFrame

today = datetime.datetime.today().strftime('%Y%m%d')

start = today
end = today

pro = ts.pro_api()

#获取行业分类
stocks = pro.stock_basic(fields='ts_code').ts_code
name = pro.stock_basic(fields='name, ts_code').set_index('ts_code')
df_daily = DataFrame()
for stock in stocks:
    df = pd.concat([
        pro.daily(ts_code=stock, start_date=start, end_date=end, fields='ts_code, trade_date, open, high, low, close, vol, amount').set_index('trade_date'),
        pro.adj_factor(ts_code=stock, start_date=start, end_date=end, fields='trade_date, adj_factor').set_index('trade_date'),
        pro.daily_basic(ts_code=stock, start_date=start, end_date=end, fields='trade_date, turnover_rate_f, pe_ttm, pb, ps_ttm, dv_ttm, total_mv, circ_mv').set_index('trade_date'),
    ], axis=1, sort=False)
    if len(df) == 0:
        continue
    df.loc[:,'st'] = ('ST' in name.loc[stock, 'name'])
    df = df.sort_index()
    if name.loc[stock, 'name'][0] == 'N':
        df.to_csv('../StockDailyData/Stock/%s.csv'%stock)
    else:
        df.to_csv('../StockDailyData/Stock/%s.csv'%stock, mode='a', header=False)
    if df.notna().iloc[-1, :].any():
        df_daily = pd.concat([df_daily, df.iloc[-1:, :]], axis=0, sort=False)
df_daily.set_index('ts_code').to_csv('../StockDailyData/Daily/%s.csv'%df.index[-1])