#!/usr/bin/env python
# encoding: utf-8
"""
@author: bingweichen
@contact: bingwei.chen11@gmail.com
@file: util.py
@time: 2018/12/12 下午5:39
@desc:

"""
import pickle
import os
import datetime


def logger(msg):
	row = '\t'.join(['[' + str(datetime.datetime.now().strftime('%m-%d %H:%M')) + ']', str(msg)])
	print(row)


def serialize(data, path):
	dir, _ = os.path.split(path)
	if not os.path.isdir(dir):
		logger('{} not exist. Creating...'.format(dir))
		os.makedirs(dir)
	with open(path, 'wb') as f:
		pickle.dump(data, f)


def deserialize(path):
	if not os.path.isfile(path):
		logger('{} not found.'.format(path))
		raise FileNotFoundError
	with open(path, 'rb') as f:
		data = pickle.load(f)
	return data
