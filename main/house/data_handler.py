#!/usr/bin/env python
# encoding: utf-8
"""
@author: bingweichen
@contact: bingwei.chen11@gmail.com
@file: main_.py
@time: 2018/12/12 下午3:43
@desc: 数据预处理

"""
import pandas as pd
import re
import numpy as np
import patsy
import statsmodels.api as sm

from config import Path
from util.util import logger, deserialize, serialize


class DataHandlerError(ValueError):
	pass


# split using the bullet
def parse_info(row):
	if not 'sqft' in row:
		br, ba = row.split('•')[:2]
		sqft = np.nan
	else:
		br, ba, sqft = row.split('•')[:3]
	return pd.Series({'Beds': br, 'Baths': ba, 'Sqft': sqft})


# parse out zip, floor
def parse_addy(r):
	so_zip = re.search(', NY(\d+)', r)
	so_flr = re.search('(?:APT|#)\s+(\d+)[A-Z]+,', r)
	if so_zip:
		zipc = so_zip.group(1)
	else:
		zipc = np.nan
	if so_flr:
		flr = so_flr.group(1)
	else:
		flr = np.nan
	return pd.Series({'Zip': zipc, 'Floor': flr})


class DataHandler(object):

	def __init__(self, config_dh):
		self.__raw_data_dir = config_dh["raw_data_dir"]

		self.__processed_data_dir = config_dh["processed_data_dir"]

		self.__processed_data_df = None

		self.__model = None

		self.__X = None

	# load processed data
	def load(self):
		self.__processed_data_df = deserialize(self.__processed_data_dir)

	def process(self):
		df = pd.read_csv(self.__raw_data_dir)
		# single units
		su = df[df['listingtype_value'].str.contains('Apartment For')]

		# select those listings with a bath
		no_baths = su[~(su['propertyinfo_value'].str.contains('ba'))]
		sucln = su[~su.index.isin(no_baths.index)]

		attr = sucln['propertyinfo_value'].apply(parse_info)
		# remove the strings from our values
		attr_cln = attr.applymap(lambda x: x.strip().split(' ')[0] if isinstance(x, str) else np.nan)

		sujnd = sucln.join(attr_cln)

		flrzip = sujnd['routable_link/_text'].apply(parse_addy)

		suf = sujnd.join(flrzip)

		# we'll reduce the data down to the columns of interest
		sudf = suf[['pricelarge_value_prices', 'Beds', 'Baths', 'Sqft', 'Floor', 'Zip']]

		# we'll also clean up the weird column name
		sudf.rename(columns={'pricelarge_value_prices': 'Rent'}, inplace=True)
		sudf.reset_index(drop=True, inplace=True)

		# we'll replace 'Studio' with 0 where present
		sudf.loc[:, 'Beds'] = sudf['Beds'].map(lambda x: 0 if 'Studio' in x else x)

		# let's fix the datatype for the columns
		sudf.loc[:, 'Rent'] = sudf['Rent'].astype(int)
		sudf.loc[:, 'Beds'] = sudf['Beds'].astype(int)

		# half baths require a float
		sudf.loc[:, 'Baths'] = sudf['Baths'].astype(float)

		# with NaNs we need float, but we have to replace commas first
		sudf.loc[:, 'Sqft'] = sudf['Sqft'].str.replace(',', '')

		sudf.loc[:, 'Sqft'] = sudf['Sqft'].astype(float)
		sudf.loc[:, 'Floor'] = sudf['Floor'].astype(float)

		sudf = sudf.drop([318])

		su_lt_two = sudf[sudf['Beds'] < 2]

		self.__processed_data_df = su_lt_two
		su_lt_two.to_csv(self.__processed_data_dir, index=False)

		serialize(data=su_lt_two, path=self.__processed_data_dir)
		# pickle.dump(model, open(path + '-sklearn', 'wb'))

		pass

	# def load(self):

	def train(self):
		f = 'Rent ~ Zip + Beds'
		y, X = patsy.dmatrices(f, self.__processed_data_df, return_type='dataframe')

		self.__X = X
		results = sm.OLS(y, X).fit()
		self.__model = results
		print(results.summary())

	def predict(self, Beds_num, zip_str):
		to_pred_idx = self.__X.iloc[0].index
		to_pred_zeros = np.zeros(len(to_pred_idx))
		tpdf = pd.DataFrame(to_pred_zeros, index=to_pred_idx, columns=['value'])
		tpdf['value'] = 0
		tpdf.loc['Intercept'] = 1
		tpdf.loc['Beds'] = Beds_num
		zip_s = 'Zip[T.{}]'.format(zip_str)
		tpdf.loc[zip_s] = 1
		pred = self.__model.predict([tpdf['value']])
		print(pred)
		return pred


# 主函数
CSV_PATH = "{}/magic.csv".format(Path.dataset_path)
config_dh = {
	"raw_data_dir": CSV_PATH,
	"processed_data_dir": "{}/processed_magic.pkl".format(Path.dataset_path)
}
data_handler = DataHandler(config_dh)
data_handler.load()
# data_handler.process()
data_handler.train()
data_handler.predict(Beds_num=2, zip_str='10002')

if __name__ == '__main__':
	pass
