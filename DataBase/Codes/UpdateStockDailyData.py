import tushare as ts
import os
import sys
import time
import datetime
import numpy as np
import pandas as pd
from pandas import Series, DataFrame

if len(sys.argv) == 2:
    today = sys.argv[1]
else:
    today = datetime.datetime.today().strftime('%Y%m%d')

start = today
end = today

pro = ts.pro_api()

#获取行业分类
stocks = pro.stock_basic(fields='ts_code').ts_code
name = pro.stock_basic(fields='name, ts_code').set_index('ts_code')
daily = pro.daily(start_date=start, end_date=end, fields='ts_code, open, high, low, close, vol, amount').set_index('ts_code')
adj_factor = pro.adj_factor(trade_date=end, fields='ts_code, adj_factor').set_index('ts_code')
#daily_basic = pro.daily_basic(trade_date=today, fields='ts_code, turnover_rate_f, pe_ttm, pb, ps_ttm, dv_ttm, total_mv, circ_mv').set_index('ts_code')

df_daily = DataFrame()

for stock in stocks:
    if (stock in list(daily.index)) and (stock in list(adj_factor.index)):
        df = pd.concat([daily.loc[[stock], :], adj_factor.loc[[stock], :], ], axis=1, sort=False)
        df.loc[:,'st'] = ('ST' in name.loc[stock, 'name'])
        df.index=[today]
        df = pd.concat([DataFrame(stock, index=[today], columns=['ts_code']), df], axis=1, sort=False)
        if os.path.exists('../StockDailyData/Stock/%s.csv'%stock):
            df.to_csv('../StockDailyData/Stock/%s.csv'%stock, mode='a', header=False)
            df_daily = pd.concat([df_daily, df.iloc[-1:, :]], axis=0, sort=False)
        else:
            if len(df) > 0:
                df.to_csv('../StockDailyData/Stock/%s.csv'%stock)
                df_daily = pd.concat([df_daily, df.iloc[-1:, :]], axis=0, sort=False)
    else:
        if os.path.exists('../StockDailyData/Stock/%s.csv'%stock):
            DataFrame(index=[today]).to_csv('../StockDailyData/Stock/%s.csv'%stock, mode='a', header=False)
df_daily.set_index('ts_code').to_csv('../StockDailyData/Daily/%s.csv'%df.index[-1])