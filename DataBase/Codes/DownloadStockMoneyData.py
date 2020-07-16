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
        pro.hk_hold(ts_code=stock).set_index('trade_date').sort_index().vol.rename('gt_vol'),
        pro.margin_detail(ts_code=stock).set_index('trade_date').loc[:, ['rzye', 'rqye']],
    ], axis=1, sort=False)
    df = df.sort_index()
    df.to_csv('../StockMoneyData/Stock/%s.csv'%stock)
    if len(df) > 0:
        if df.notna().iloc[-1, 0]:
            df_daily = pd.concat([df_daily, df.iloc[-1:, :]], axis=0, sort=False)
df_daily.set_index('ts_code').to_csv('../StockMoneyData/Daily/%s.csv'%today)