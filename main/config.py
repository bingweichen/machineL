import os


def add_path(path):
	return os.path.join(os.path.dirname(__file__) + '/{}'.format(path))


# 文件路径
class Path:
	chromedriver_path = add_path('../package/chromedriver')
	crawler_data = add_path('./crawler/data')
	dataset_path = add_path('../dataset')

	phantomjs_path = add_path("../package/phantomjs-2.1.1-macosx/bin/phantomjs")
