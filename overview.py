import requests
import pandas as pd
import os

PATH = './data/iris/'
starred_url = 'https://api.github.com/users/acombs/starred'
iris_url = 'https://archive.ics.uci.edu/ml/machine-learning-' \
           'databases/iris/iris.data'


# r = requests.get()
# r.json()

def download_data():
    r = requests.get(iris_url)
    with open(PATH + 'iris.data', 'w') as f:
        f.write(r.text)


def read_data():
    df = pd.read_csv(PATH + 'iris.data',
                     names=["sepal length", "sepal width",
                            "petal length", "petal width", "class"])


# class PandasFunc():
#     def others(self):
#         self.ipos.sort_values('Trade Date', inplace=True)

# 一些pandas用法记录
def read_excel():
    excel_path = '/Users/chen/myPoject/gitRepo/machineL/dataset/ipos.xlsx'
    xls = pd.ExcelFile(excel_path)
    exchanges = xls.sheet_names
    ipos = pd.read_excel(xls, sheet_name=exchanges[0], encoding='latin-1')

    ipos_1 = pd.read_csv(
        r'/Users/chen/myPoject/gitRepo/machineL/dataset/ipos.csv')


def others(ipos):
    ipos.sort_values('Trade Date', inplace=True)
    ipos.to_csv("/Users/chen/myPoject/gitRepo/machineL/dataset/ipos.csv",
                index=False)

    ipos.rename(columns={'old': 'new'}, inplace=True)
