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
df_daily = DataFrame()
for stock in stocks:
    df = pd.concat([
        pro.hk_hold(ts_code=stock, start_date=start, end_date=end).set_index('trade_date').sort_index().vol.rename('gt_vol'),
        pro.margin_detail(ts_code=stock, start_date=start, end_date=end).set_index('trade_date').loc[:, ['rzye', 'rqye']],
        pro.moneyflow(ts_code=stock, start_date=start, end_date=end, fields='trade_date, ts_code, buy_sm_amount, sell_sm_amount, buy_md_amount, sell_md_amount, buy_lg_amount, sell_lg_amount, buy_elg_amount, sell_elg_amount, net_mf_amount').set_index('trade_date'),
    ], axis=1, sort=False)
    df = df.sort_index()
    df.to_csv('../StockMoneyData/Stock/%s.csv'%stock, mode='a', header=False)
    if len(df) > 0:
        if df.notna().iloc[-1, :].any():
            df_daily = pd.concat([df_daily, df.iloc[-1:, :]], axis=0, sort=False)
df_daily.set_index('ts_code').to_csv('../StockMoneyData/Daily/%s.csv'%df.index[-1])