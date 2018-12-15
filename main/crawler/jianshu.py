from selenium import webdriver
import time
from config import Path


def crawler_jianshu():
	url = "https://www.jianshu.com/"
	chromedriver_path = Path.chromedriver_path
	save_file_path = "{}/article_jianshu.txt".format(Path.crawler_data)

	options = webdriver.ChromeOptions()
	options.add_argument('headless')
	browser = webdriver.Chrome(
		chromedriver_path,
		options=options
	)
	browser.get(url)

	for i in range(3):
		browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # execute_script是插入js代码的
		time.sleep(2)  # 加载需要时间，2秒比较合理

		for j in range(10):  # 这里我模拟10次点击
			try:
				button = browser.execute_script("var a = document.getElementsByClassName('load-more'); a[0].click();")
				time.sleep(2)
			except:
				pass

	titles = browser.find_elements_by_class_name("title")

	with open(save_file_path, "w", encoding="utf-8") as f:
		for t in titles:
			try:
				f.write(t.text + " " + t.get_attribute("href"))
				f.write("\n")
			except TypeError:
				pass


if __name__ == '__main__':
	crawler_jianshu()
	pass
