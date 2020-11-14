import tushare as ts
import os
import sys
import time
import datetime
import numpy as np
import pandas as pd
from pandas import Series, DataFrame

today = datetime.datetime.today().strftime('%Y%m%d')

if len(sys.argv) > 1:
    start = sys.argv[1]
else:
    start = '20150101'
end = today

pro = ts.pro_api()

#获取行业分类
stocks = pro.stock_basic(fields='ts_code').ts_code
df_daily = DataFrame()
for stock in stocks:
    df = pd.concat([
        pro.daily(ts_code=stock, start_date=start, end_date=end, fields='ts_code, trade_date, open, high, low, close, vol, amount').set_index('trade_date'),
        pro.adj_factor(ts_code=stock, start_date=start, end_date=end, fields='trade_date, adj_factor').set_index('trade_date'),
    ], axis=1, sort=False)
    st = DataFrame(False, index=df.index, columns=[stock])
    nc = pro.namechange(ts_code=stock)
    for i in nc.index:
        if 'ST' in nc.loc[i, 'name']:
            if nc.loc[i, 'end_date'] == None:
                st.loc[nc.loc[i, 'start_date'] <= st.index, stock] = True
            else:
                st.loc[(nc.loc[i, 'start_date'] <= st.index) & (st.index <= nc.loc[i, 'end_date']), stock] = True
    st.columns = ['st']
    df = pd.concat([df, st], axis=1, sort=False)
    df = df.sort_index()
    
    if len(df) > 0:
        df.to_csv('../StockDailyData/Stock/%s.csv'%stock)
        if df.notna().iloc[-1, :].any():
            df_daily = pd.concat([df_daily, df.iloc[-1:, :]], axis=0, sort=False)
df_daily.set_index('ts_code').to_csv('../StockDailyData/Daily/%s.csv'%df.index[-1])


#pro.daily_basic(ts_code=stock, start_date=start, end_date=end, fields='trade_date, turnover_rate_f, pe_ttm, pb, ps_ttm, dv_ttm, total_mv, circ_mv').set_index('trade_date'),