#!/usr/bin/env python
# encoding: utf-8
"""
@author: bingweichen
@contact: bingwei.chen11@gmail.com
@file: main.py.py
@time: 2018/12/13 上午11:05
@desc:


"""

from config import Path
from util import *

csv_path = "{}/spy.csv".format(Path.dataset_path)

import pandas as pd
from sklearn import linear_model
from patsy import dmatrix
from sklearn.ensemble import RandomForestClassifier


class IPO(object):
    def __init__(self):
        self.__ipo_csv_path = "{}/ipos.csv".format(Path.dataset_path)
        self.__sp_csv_path = "{}/spy.csv".format(Path.dataset_path)
        self.__ipos = pd.read_csv(self.__ipo_csv_path)
        self.__sp = pd.read_csv(self.__sp_csv_path)

        self.__clf = None
        self.__X_train = None
        self.__X_test = None
        self.__y_train = None
        self.__y_test = None

    def rename_col(self):
        pass

    def format_type(self):
        ipos = self.__ipos
        ipos['Date'] = pd.to_datetime(ipos['Date'])
        ipos['Offer Price'] = ipos['Offer Price'].astype('float')
        ipos['Opening Price'] = ipos['Opening Price'].astype('float')
        ipos['1st Day Close'] = ipos['1st Day Close'].astype('float')
        ipos['1st Day % Px Chng '] = ipos['1st Day % Px Chng '].astype('float')
        ipos['$ Chg Close'] = ipos['$ Chg Close'].astype('float')
        ipos['$ Chg Opening'] = ipos['$ Chg Opening'].astype('float')
        ipos['Star Ratings'] = ipos['Star Ratings'].astype('int')
        self.__ipos = ipos

    def add_feature(self):
        ipos = self.__ipos
        ipos['$ Chg Open to Close'] = ipos['$ Chg Close'] - ipos['$ Chg Opening']
        ipos['% Chg Open to Close'] = (ipos['$ Chg Open to Close'] / ipos['Opening Price']) * 100
        self.__ipos = ipos

    def remove_error_data(self):
        self.__ipos.loc[440, '$ Chg Opening'] = .09
        self.__ipos.loc[1264, '$ Chg Opening'] = .01
        self.__ipos.loc[1264, 'Opening Price'] = 11.26

    def remove_error_date(self):
        self.__ipos.loc[1175, 'Date'] = pd.to_datetime('2009-08-12')
        self.__ipos.loc[1865, 'Date'] = pd.to_datetime('2013-11-06')
        self.__ipos.loc[2251, 'Date'] = pd.to_datetime('2015-05-21')
        self.__ipos.loc[2252, 'Date'] = pd.to_datetime('2015-05-21')

    def process_data(self):
        # todo 删掉多余的行
        self.rename_col()
        ipos = self.__ipos
        ipos.replace('N/C', 0, inplace=True)
        self.format_type()
        self.add_feature()

        # 特征提取
        self.remove_error_date()
        ipos['SP Week Change'] = ipos['Date'].map(self.get_week_chg)
        ipos['SP Close to Open Chg Pct'] = ipos['Date'].map(self.get_cto_chg)

        self.format_name()
        # 领投公司数量
        ipos['Total Underwriters'] = ipos['Lead/Joint-Lead Mangager'].map(lambda x: len(x.split('/')))
        # 周 月
        ipos['Week Day'] = ipos['Date'].dt.dayofweek.map(
            {0: 'Mon', 1: 'Tues', 2: 'Wed', 3: 'Thurs', 4: 'Fri', 5: 'Sat', 6: 'Sun'})
        ipos['Month'] = ipos['Date'].map(lambda x: x.month)
        ipos['Month'] = ipos['Month'].map(
            {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct',
             11: 'Nov', 12: 'Dec'})

        # 感觉加过了？
        ipos['Gap Open Pct'] = (ipos['$ Chg Opening'].astype('float') / ipos['Opening Price'].astype('float')) * 100
        ipos['Open to Close Pct'] = (ipos['$ Chg Close'].astype('float') - ipos['$ Chg Opening'].astype('float')) / \
                                    ipos['Opening Price'].astype('float') * 100
        self.__ipos = ipos
        pass

    def get_cto_chg(self, ipo_dt):
        sp = self.__sp
        try:
            today_open_idx = sp[sp['Date'] == str(ipo_dt.date())].index[0]
            yday_close_idx = sp[sp['Date'] == str(ipo_dt.date())].index[0] - 1
            chg = (sp.iloc[today_open_idx]['Open'] - sp.iloc[yday_close_idx]['Close']) / (
                sp.iloc[yday_close_idx]['Close'])
            return chg * 100
        except:
            print('error', ipo_dt)

    def get_week_chg(self, ipo_dt):
        sp = self.__sp
        try:
            day_ago_idx = sp[sp['Date'] == str(ipo_dt.date())].index[0] - 1
            week_ago_idx = sp[sp['Date'] == str(ipo_dt.date())].index[0] - 16
            chg = (sp.iloc[day_ago_idx]['Close'] - sp.iloc[week_ago_idx]['Close']) / \
                  (sp.iloc[week_ago_idx]['Close'])
            return chg * 100
        except:
            print('error', ipo_dt.date())

    def train_test_split(self):
        ipos = self.__ipos
        X = dmatrix('Month + Q("Week Day") + Q("Total Underwriters") + Q("Gap Open Pct") + Q("$ Chg Opening") +\
                  Q("Lead Mgr") + Q("Offer Price") + Q("Opening Price") +\
                  Q("SP Close to Open Chg Pct") + Q("SP Week Change")', data=ipos, return_type='dataframe')
        # Index of first 2015 IPO is 2188, 2014 is 1900
        idx = 2188
        X_train, X_test = X[:idx], X[idx:]
        y_train = ipos['$ Chg Open to Close'][:idx].map(lambda x: 1 if x >= .25 else 0)
        y_test = ipos['$ Chg Open to Close'][idx:].map(lambda x: 1 if x >= .25 else 0)

        self.__X_train = X_train
        self.__X_test = X_test
        self.__y_train = y_train
        self.__y_test = y_test

    def train(self):
        clf = linear_model.LogisticRegression()
        clf.fit(self.__X_train, self.__y_train)
        self.__clf = clf

    def random_forest_train(self):
        clf_rf = RandomForestClassifier(n_estimators=5000)
        model = clf_rf.fit(self.__X_train, self.__y_train)
        self.__clf = model
        # clf_rf.score(X_test, y_test)

    def test(self):
        score = self.__clf.score(self.__X_test, self.__y_test)
        logger("score", score)

    def predict(self):
        y_test = self.__y_test
        ipos = self.__ipos
        pred_label = self.__clf.predict(self.__X_test)
        results = []
        for pl, tl, idx, chg in zip(pred_label, y_test, y_test.index, ipos.ix[y_test.index]['$ Chg Open to Close']):
            if pl == tl:
                results.append([idx, chg, pl, tl, 1])
            else:
                results.append([idx, chg, pl, tl, 0])
        rf = pd.DataFrame(results, columns=['index', '$ chg', 'predicted', 'actual', 'correct'])
        logger("rf", rf[rf['predicted'] == 1]['$ chg'].sum())
        logger("rf", ipos[(ipos['Date'] >= '2015-01-01')]['$ Chg Open to Close'].sum())

    def main(self):
        self.process_data()
        self.train_test_split()
        self.train()
        self.test()
        pass

    def format_name(self):
        """
        把相同的 Lead Mgr 设置成一样的名字
        :return:
        """
        ipos = self.__ipos
        ipos['Lead Mgr'] = ipos['Lead/Joint-Lead Mangager'].map(lambda x: x.split('/')[0])
        ipos['Lead Mgr'] = ipos['Lead Mgr'].map(lambda x: x.strip())
        ipos.loc[ipos['Lead Mgr'].str.contains('Hambrecht'), 'Lead Mgr'] = 'WR Hambrecht+Co.'
        ipos.loc[ipos['Lead Mgr'].str.contains('Edwards'), 'Lead Mgr'] = 'AG Edwards'
        ipos.loc[ipos['Lead Mgr'].str.contains('Edwrads'), 'Lead Mgr'] = 'AG Edwards'
        ipos.loc[ipos['Lead Mgr'].str.contains('Barclay'), 'Lead Mgr'] = 'Barclays'
        ipos.loc[ipos['Lead Mgr'].str.contains('Aegis'), 'Lead Mgr'] = 'Aegis Capital'
        ipos.loc[ipos['Lead Mgr'].str.contains('Deutsche'), 'Lead Mgr'] = 'Deutsche Bank'
        ipos.loc[ipos['Lead Mgr'].str.contains('Suisse'), 'Lead Mgr'] = 'CSFB'
        ipos.loc[ipos['Lead Mgr'].str.contains('CS.?F'), 'Lead Mgr'] = 'CSFB'
        ipos.loc[ipos['Lead Mgr'].str.contains('^Early'), 'Lead Mgr'] = 'EarlyBirdCapital'
        ipos.loc[325, 'Lead Mgr'] = 'Maximum Captial'
        ipos.loc[ipos['Lead Mgr'].str.contains('Keefe'), 'Lead Mgr'] = 'Keefe, Bruyette & Woods'
        ipos.loc[ipos['Lead Mgr'].str.contains('Stan'), 'Lead Mgr'] = 'Morgan Stanley'
        ipos.loc[ipos['Lead Mgr'].str.contains('P. Morg'), 'Lead Mgr'] = 'JP Morgan'
        ipos.loc[ipos['Lead Mgr'].str.contains('PM'), 'Lead Mgr'] = 'JP Morgan'
        ipos.loc[ipos['Lead Mgr'].str.contains('J\.P\.'), 'Lead Mgr'] = 'JP Morgan'
        ipos.loc[ipos['Lead Mgr'].str.contains('Banc of'), 'Lead Mgr'] = 'Banc of America'
        ipos.loc[ipos['Lead Mgr'].str.contains('Lych'), 'Lead Mgr'] = 'BofA Merrill Lynch'
        ipos.loc[ipos['Lead Mgr'].str.contains('Merrill$'), 'Lead Mgr'] = 'Merrill Lynch'
        ipos.loc[ipos['Lead Mgr'].str.contains('Lymch'), 'Lead Mgr'] = 'Merrill Lynch'
        ipos.loc[ipos['Lead Mgr'].str.contains('A Merril Lynch'), 'Lead Mgr'] = 'BofA Merrill Lynch'
        ipos.loc[ipos['Lead Mgr'].str.contains('Merril '), 'Lead Mgr'] = 'Merrill Lynch'
        ipos.loc[ipos['Lead Mgr'].str.contains('BofA$'), 'Lead Mgr'] = 'BofA Merrill Lynch'
        ipos.loc[ipos['Lead Mgr'].str.contains('SANDLER'), 'Lead Mgr'] = 'Sandler O\'neil + Partners'
        ipos.loc[ipos['Lead Mgr'].str.contains('Sandler'), 'Lead Mgr'] = 'Sandler O\'Neil + Partners'
        ipos.loc[ipos['Lead Mgr'].str.contains('Renshaw'), 'Lead Mgr'] = 'Rodman & Renshaw'
        ipos.loc[ipos['Lead Mgr'].str.contains('Baird'), 'Lead Mgr'] = 'RW Baird'
        ipos.loc[ipos['Lead Mgr'].str.contains('Cantor'), 'Lead Mgr'] = 'Cantor Fitzgerald'
        ipos.loc[ipos['Lead Mgr'].str.contains('Goldman'), 'Lead Mgr'] = 'Goldman Sachs'
        ipos.loc[ipos['Lead Mgr'].str.contains('Bear'), 'Lead Mgr'] = 'Bear Stearns'
        ipos.loc[ipos['Lead Mgr'].str.contains('BoA'), 'Lead Mgr'] = 'BofA Merrill Lynch'
        ipos.loc[ipos['Lead Mgr'].str.contains('Broadband'), 'Lead Mgr'] = 'Broadband Capital'
        ipos.loc[ipos['Lead Mgr'].str.contains('Davidson'), 'Lead Mgr'] = 'DA Davidson'
        ipos.loc[ipos['Lead Mgr'].str.contains('Feltl'), 'Lead Mgr'] = 'Feltl & Co.'
        ipos.loc[ipos['Lead Mgr'].str.contains('China'), 'Lead Mgr'] = 'China International'
        ipos.loc[ipos['Lead Mgr'].str.contains('Cit'), 'Lead Mgr'] = 'Citigroup'
        ipos.loc[ipos['Lead Mgr'].str.contains('Ferris'), 'Lead Mgr'] = 'Ferris Baker Watts'
        ipos.loc[ipos['Lead Mgr'].str.contains('Friedman|Freidman|FBR'), 'Lead Mgr'] = 'Friedman Billings Ramsey'
        ipos.loc[ipos['Lead Mgr'].str.contains('^I-'), 'Lead Mgr'] = 'I-Bankers'
        ipos.loc[ipos['Lead Mgr'].str.contains('Gunn'), 'Lead Mgr'] = 'Gunn Allen'
        ipos.loc[ipos['Lead Mgr'].str.contains('Jeffer'), 'Lead Mgr'] = 'Jefferies'
        ipos.loc[ipos['Lead Mgr'].str.contains('Oppen'), 'Lead Mgr'] = 'Oppenheimer'
        ipos.loc[ipos['Lead Mgr'].str.contains('JMP'), 'Lead Mgr'] = 'JMP Securities'
        ipos.loc[ipos['Lead Mgr'].str.contains('Rice'), 'Lead Mgr'] = 'Johnson Rice'
        ipos.loc[ipos['Lead Mgr'].str.contains('Ladenburg'), 'Lead Mgr'] = 'Ladenburg Thalmann'
        ipos.loc[ipos['Lead Mgr'].str.contains('Piper'), 'Lead Mgr'] = 'Piper Jaffray'
        ipos.loc[ipos['Lead Mgr'].str.contains('Pali'), 'Lead Mgr'] = 'Pali Capital'
        ipos.loc[ipos['Lead Mgr'].str.contains('Paulson'), 'Lead Mgr'] = 'Paulson Investment Co.'
        ipos.loc[ipos['Lead Mgr'].str.contains('Roth'), 'Lead Mgr'] = 'Roth Capital'
        ipos.loc[ipos['Lead Mgr'].str.contains('Stifel'), 'Lead Mgr'] = 'Stifel Nicolaus'
        ipos.loc[ipos['Lead Mgr'].str.contains('SunTrust'), 'Lead Mgr'] = 'SunTrust Robinson'
        ipos.loc[ipos['Lead Mgr'].str.contains('Wachovia'), 'Lead Mgr'] = 'Wachovia'
        ipos.loc[ipos['Lead Mgr'].str.contains('Wedbush'), 'Lead Mgr'] = 'Wedbush Morgan'
        ipos.loc[ipos['Lead Mgr'].str.contains('Blair'), 'Lead Mgr'] = 'William Blair'
        ipos.loc[ipos['Lead Mgr'].str.contains('Wunderlich'), 'Lead Mgr'] = 'Wunderlich'
        ipos.loc[ipos['Lead Mgr'].str.contains('Max'), 'Lead Mgr'] = 'Maxim Group'
        ipos.loc[ipos['Lead Mgr'].str.contains('CIBC'), 'Lead Mgr'] = 'CIBC'
        ipos.loc[ipos['Lead Mgr'].str.contains('CRT'), 'Lead Mgr'] = 'CRT Capital'
        ipos.loc[ipos['Lead Mgr'].str.contains('HCF'), 'Lead Mgr'] = 'HCFP Brenner'
        ipos.loc[ipos['Lead Mgr'].str.contains('Cohen'), 'Lead Mgr'] = 'Cohen & Co.'
        ipos.loc[ipos['Lead Mgr'].str.contains('Cowen'), 'Lead Mgr'] = 'Cowen & Co.'
        ipos.loc[ipos['Lead Mgr'].str.contains('Leerink'), 'Lead Mgr'] = 'Leerink Partners'
        ipos.loc[ipos['Lead Mgr'].str.contains('Lynch\xca'), 'Lead Mgr'] = 'Merrill Lynch'
        self.__ipos = ipos


ipo = IPO()
ipo.process_data()
# ipo.main()

if __name__ == '__main__':
    pass
