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

csv_path = "{}/spy.csv".format(Path.dataset_path)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model
from patsy import dmatrix

# %matplotlib inline
sp = pd.read_csv(csv_path)
sp.sort_values('Date', inplace=True)
sp.reset_index(drop=True, inplace=True)

all_dates = sp[['Date']]
tkr_index = [x for x in all_dates.index if x % 15 == 0]



if __name__ == '__main__':
    pass
