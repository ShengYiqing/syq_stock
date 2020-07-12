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
    start = '20100101'
end = today

pro = ts.pro_api()

#获取行业分类
stocks = pro.stock_basic(fields='ts_code').ts_code
df_daily = DataFrame()
for stock in stocks:
    df = pd.concat([
        pro.daily(ts_code=stock, start_date=start, end_date=end, fields='ts_code, trade_date, open, high, low, close, vol').set_index('trade_date'),
        pro.adj_factor(ts_code=stock, start_date=start, end_date=end, fields='trade_date, adj_factor').set_index('trade_date'),
        pro.daily_basic(ts_code=stock, start_date=start, end_date=end, fields='trade_date, turnover_rate_f, volume_ratio, pe_ttm, pb, ps_ttm, total_mv, circ_mv').set_index('trade_date'),
        pro.moneyflow(ts_code=stock, start_date=start, end_date=end, fields='trade_date, buy_sm_vol, sell_sm_vol, buy_md_vol, sell_md_vol, buy_lg_vol, sell_lg_vol, buy_elg_vol, sell_elg_vol, net_mf_vol').set_index('trade_date'),
    ], axis=1, sort=False)
    df = df.sort_index()
    '''
    df = pro.daily(ts_code=stock, start_date=start, end_date=end).set_index('trade_date')
    df.loc[:, 'adj_factor'] = pro.adj_factor(ts_code=stock, start_date=start, end_date=end).set_index('trade_date').adj_factor
    df = pd.concat([df, pro.daily_basic(ts_code=stock, start_date=start, end_date=end, fields='trade_date, turnover_rate, turnover_rate_f, volume_ratio, pe_ttm, pb, ps_ttm, total_mv, circ_mv').set_index('trade_date')], axis=1, sort=False)
    df = pd.concat([df, pro.moneyflow(ts_code=stock, start_date=start, end_date=end, fields='trade_date, buy_sm_vol, sell_sm_vol, buy_md_vol, sell_md_vol, buy_lg_vol, sell_lg_vol, buy_elg_vol, sell_elg_vol, net_mf_vol').set_index('trade_date')], axis=1, sort=False)
    df = df.sort_index()
    '''
    df.to_csv('../StockDailyData/Stock/%s.csv'%stock)
    if len(df) > 0:
        if df.notna().iloc[-1, 0]:
            df_daily = pd.concat([df_daily, df.iloc[-1:, :]], axis=0, sort=False)
df_daily.set_index('ts_code').to_csv('../StockDailyData/Daily/%s.csv'%today)