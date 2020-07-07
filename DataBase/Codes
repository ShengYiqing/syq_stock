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
    start = '20000101'
end = today

pro = ts.pro_api()

#获取行业分类
industry = {i:pro.index_member(index_code=i).con_code.values for i in pro.index_classify(level='L1', src='SW').sort_values('index_code').loc[:, 'index_code']}

for i in industry.keys():
    if os.path.exists('../StockDailyData/%s'%i):
        pass
    else:
        os.mkdir('../StockDailyData/%s'%i)
    for stock in industry[i]:
        df = pro.daily(ts_code=stock, start_date=start, end_data=end).set_index('trade_date')
        df.loc[:, 'adj_factor'] = pro.adj_factor(ts_code=stock, start_date=start, end_date=end).set_index('trade_date').adj_factor
        df.to_csv('../StockDailyData/%s/%s.csv'%(i, stock))
