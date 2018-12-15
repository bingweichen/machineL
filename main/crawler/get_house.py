import bs4
import requests
import time
from util.util import logger, deserialize, serialize
from config import Path

heads = {
	"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
}

house_list_urls = ["http://sh.xiaozhu.com/search-duanzufang-p{}-0/".format(str(i)) for i in range(1, 12)]


def get_house_info(url):
	response = requests.get(url, headers=heads)
	time.sleep(2)
	soup = bs4.BeautifulSoup(response.text, "lxml")

	title = soup.select('div.pho_info > h4 > em')[0].get_text()
	address = soup.select('div.pho_info > p')[0].get('title')
	price = soup.select('div.day_l > span')[0].get_text()
	avator = soup.select('div.member_pic > a > img')[0].get('src')
	sex = soup.select('div.member_pic > div')[0].get('class')[0]
	sex = "male" if sex == "member_ico" else "female"
	lord = soup.select("a.lorder_name")[0].get_text()
	# print(title, address, price, avator, sex, lord)
	return {
		title, address, price, avator, sex, lord
	}


def get_houses(url):
	response = requests.get(url, headers=heads)
	soup = bs4.BeautifulSoup(response.text, 'lxml')
	house_list = [i.parent.get('href') for i in soup.select('img.lodgeunitpic')]

	data = []
	for i in house_list:
		row = get_house_info(i)
		data.append(row)
	# 存成pickle 或者csv
	serialize(data=data, path="{}/houses.pkl".format(Path.dataset_path))


if __name__ == '__main__':
	for i in house_list_urls:
		get_houses(i)
