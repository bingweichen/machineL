#!/usr/bin/env python
# encoding: utf-8
"""
@author: bingweichen
@contact: bingwei.chen11@gmail.com
@file: pandas_practise.py
@time: 2018/12/25 下午3:03
@desc:

"""

import pandas as pd


def practise():
    # 读入
    df = pd.read_csv('newcsv2.csv', index_col=0)
    # 保存
    df.to_csv('newcsv2.csv', index=False)
    # 设置索引
    df.set_index('Day', inplace=True)
    # 操作

    # 重命名
    df.rename({"old_name": "new_name"}, axis='columns', inplace=True)
    # 删除
    df.drop([1335], inplace=True)  # 原有数据块也删除
    # 选取
    df.loc[:, ['A', 'B']]
    df.iloc[[1, 3, 5], 1:3]
    sp.loc[list(range(3,8))+[12]]

    # 错误排查
    def print_ipo(row):
        try:
            result = pd.to_datetime(row["Trade Date"])
        except:
            print(row.index)
            print(row)

    df.apply(print_ipo, axis=1)
    pass

# import datetime
# import pandas_datareader.data as web
# start = datetime.datetime(2010, 1, 1)
# end = datetime.datetime(2015, 8, 22)
#
# df = web.DataReader("XOM", "yahoo", start, end)
#
# print(df)
#
# import matplotlib.pyplot as plt
# from matplotlib import style
#
# style.use('fivethirtyeight')
