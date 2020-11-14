import time
import datetime
import os
import sys
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
import tools
import tushare as ts
from scipy.stats import rankdata

class SingleFactor:
    def __init__(self, factor_name, stocks=None, start_date=None, end_date=None):
        self.factor_name = factor_name
        self.stocks = stocks
        self.start_date = start_date
        self.end_date = end_date
        
        self.factor = None
        
        y1 = pd.read_csv('../../FactorBase/y/Data/y1.csv', index_col=[0], parse_dates=[0]).loc[:, stocks]
        y2 = pd.read_csv('../../FactorBase/y/Data/y2.csv', index_col=[0], parse_dates=[0]).loc[:, stocks]
        y3 = pd.read_csv('../../FactorBase/y/Data/y3.csv', index_col=[0], parse_dates=[0]).loc[:, stocks]
        y4 = pd.read_csv('../../FactorBase/y/Data/y4.csv', index_col=[0], parse_dates=[0]).loc[:, stocks]
        y5 = pd.read_csv('../../FactorBase/y/Data/y5.csv', index_col=[0], parse_dates=[0]).loc[:, stocks]
        
        if start_date:
            y1 = y1.loc[y1.index >= start_date, :]
            y2 = y2.loc[y2.index >= start_date, :]
            y3 = y3.loc[y3.index >= start_date, :]
            y4 = y4.loc[y4.index >= start_date, :]
            y5 = y5.loc[y5.index >= start_date, :]
            
        if end_date:
            y1 = y1.loc[y1.index <= end_date, :]
            y2 = y2.loc[y2.index <= end_date, :]
            y3 = y3.loc[y3.index <= end_date, :]
            y4 = y4.loc[y4.index <= end_date, :]
            y5 = y5.loc[y5.index <= end_date, :]
            
        self.y1 = y1
        self.y2 = y2
        self.y3 = y3
        self.y4 = y4
        self.y5 = y5
        
    def generate_factor(self):
        self.factor = None
    
    def factor_analysis(self, industry_neutral=True, size_neutral=True):
        #行业中性、市值中性
        #IC、IR、互信息、分组回测
        
        #行业中性
        if industry_neutral:
            industrys = tools.get_industrys('L1', self.stocks)
            tmp = {}
            for k in industrys.keys():
                if len(industrys[k]) > 0:
                    tmp[k] = industrys[k]
            industrys = tmp
            factor = tools.standardize_industry(self.factor, industrys)
        self.factor_industry_neutral = factor.copy()
        
        #市值中性
        if size_neutral:
            market_capitalization = DataFrame({stock: pd.read_csv('../../DataBase/StockFundamentalsData/Stock/%s.csv'%stock, index_col=[0], parse_dates=[0]).loc[:, 'TOTMKTCAP'] for stock in self.stocks})
            market_capitalization = market_capitalization.loc[market_capitalization.index >= self.start_date, :]
            market_capitalization = market_capitalization.loc[market_capitalization.index <= self.end_date, :]
            if industry_neutral:
                market_capitalization = tools.standardize_industry(market_capitalization, industrys)
            beta = (factor * market_capitalization).sum(1) / (market_capitalization * market_capitalization).sum(1)
            factor = factor - market_capitalization.mul(beta, axis=0)
        self.factor_industry_size_neutral = factor.copy()
        
        #IC、IR、分组回测
        ys = [self.y1, self.y2, self.y3, self.y4, self.y5]
        IC = {}
        IR = {}
        group_backtest = {}
        group_pos = {}
        for i in range(len(ys)):
            y_neutral = tools.standardize_industry(ys[i], industrys)
            IC[i] = (y_neutral * factor).mean(1) / factor.std(1) / y_neutral.std(1)
            IR[i] = IC[i].rolling(20).mean() / IC[i].rolling(20).std()
            factor_quantile = pd.concat([DataFrame(rankdata(factor.loc[:, industrys[k]], axis=1), index=factor.loc[:, industrys[k]].index, columns=factor.loc[:, industrys[k]].columns) / len(industrys[k]) for k in industrys.keys()], axis=1)
            num_group = 10
            group_backtest[i] = {}
            group_pos[i] = {}
            for n in range(num_group):
                group_pos[i][n] = DataFrame((n/10 <= factor_quantile) & (factor_quantile <= (n+1)/10), dtype=int)
                group_pos[i][n] = group_pos[i][n].mul(len(group_pos[i][n].columns) / group_pos[i][n].sum(1), axis=0)
                group_backtest[i][n] = ((group_pos[i][n] * ys[i]).mean(1) - ys[i].mean(1)).cumsum().rename('%s'%(n/num_group))
        self.IC = IC
        self.IR = IR
        self.group_pos = group_pos
        self.group_backtest = group_backtest
        if not os.path.exists('../Results/%s'%self.factor_name):
            os.mkdir('../Results/%s'%self.factor_name)
        plt.figure(figsize=(16,12))
        
        for i in range(len(ys)):
            IC[i].cumsum().plot()
        plt.legend(['%s'%i for i in range(len(ys))])
        plt.savefig('../Results/%s/IC.png'%self.factor_name)
        plt.figure(figsize=(16,12))
        for i in range(len(ys)):
            IR[i].cumsum().plot()
        plt.legend(['%s'%i for i in range(len(ys))])
        plt.savefig('../Results/%s/IR.png'%self.factor_name)
        for i in range(len(ys)):
            plt.figure(figsize=(16,12))
            for n in range(num_group):
                group_backtest[i][n].plot()
            plt.legend(['%s'%i for i in range(num_group)])
            plt.savefig('../Results/%s/groupbacktest%s.png'%(self.factor_name, i))