# 在 ipynb 实现一次 成功了
# py 实现一次
# 写成 class

import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import patsy
import statsmodels.api as sm

from main.config import Path

pd.set_option("display.max_columns", 30)
pd.set_option("display.max_colwidth", 100)
pd.set_option("display.precision", 3)

plt.style.use('ggplot')

CSV_PATH = "{}/magic.csv".format(Path.dataset_path)


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


def pre_process():
	df = pd.read_csv(CSV_PATH)
	# multiple units
	mu = df[df['listingtype_value'].str.contains('Apartments For')]
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


	# train
	f = 'Rent ~ Zip + Beds'
	y, X = patsy.dmatrices(f, su_lt_two, return_type='dataframe')
	results = sm.OLS(y, X).fit()
	print(results.summary())

	# predict
	to_pred_idx = X.iloc[0].index
	to_pred_zeros = np.zeros(len(to_pred_idx))
	tpdf = pd.DataFrame(to_pred_zeros, index=to_pred_idx, columns=['value'])
	tpdf['value'] = 0
	tpdf.loc['Intercept'] = 1
	tpdf.loc['Beds'] = 2
	tpdf.loc['Zip[T.10002]'] = 1
	pred = results.predict([tpdf['value']])
	print(pred)


def train(su_lt_two):
	import patsy
	import statsmodels.api as sm
	f = 'Rent ~ Zip + Beds'
	y, X = patsy.dmatrices(f, su_lt_two, return_type='dataframe')
	results = sm.OLS(y, X).fit()
	print(results.summary())


def predict():
	pass


if __name__ == '__main__':
	pre_process()
