import requests
from bs4 import BeautifulSoup
import csv
import subprocess

URL = 'https://www.citilink.ru/catalog/mobile/smartfony/'
HEADERS = {'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.234', 'accept':'*/*'}
HOST = 'https://www.citilink.ru'
PAGES = 2
FILE = 'Citylink.csv'

def get_html(url, params = None):
	# get html code from url
	r = requests.get(url, headers = HEADERS, params = params)
	r.encoding = 'UTF-8'
	return r


def get_price(item, sale = True):
	if sale:
		try:
			p = item.find('span', class_ = 'subcategory-product-item__price subcategory-product-item__price_standart').get_text(strip = True).replace('\n\t\t', '')
			return p
		except AttributeError:
			return False
	else:
		try:
			p_o = item.find('span', class_ = 'subcategory-product-item__price subcategory-product-item__price_old').get_text(strip = True).replace('\n\t\t', '')
			return p_o
		except AttributeError:
			return 'Скидок нет'


def get_content(html):
	# get info for table

	soup = BeautifulSoup(html, 'html.parser')
	items = soup.find_all('div', class_ = 'subcategory-product-item__body')
	phones = []

	for item in items:
		phones.append({
			'title' : item.find('a', class_= 'link_gtm-js link_pageevents-js ddl_product_link').get('title').replace('&nbsp;', '').replace(',', ' '),
			'link' : item.find('a', class_= 'link_gtm-js link_pageevents-js ddl_product_link').get('href'),
			'price_sale' : get_price(item) ,
			'price_old' : get_price(item, sale = False)})
		if phones[-1]['price_sale'] == False:
			del phones[-1]
	return phones

def save_in_file(items, path):
	# save info from web-site in csv table

	with open(path, 'w', newline = '') as file:
		writer = csv.writer(file, delimiter = ';')
		writer.writerow(['Название', 'Ссылка', 'Цена', 'Цена без скидки'])
		for item in items:
			writer.writerow([item['title'], item['link'], item['price_sale'], item['price_old']])

def sorti():
	models = {0 : '',1:'1376_214ALCATEL', 2:'1376_214APPLE', 3:'1376_214BQ', 4:'1376_214DIGMA', 5:'1376_214HAIER', 6:'1376_214HONOR', 7:'1376_214HTC', 8:'1376_214HUAWEI', 9:'1376_214MEIZU', 10:'1376_214MOTOROLA', 11:'1376_214NOKIA', 12:'1376_214OPPO', 13:'1376_214PHILIPS', 14:'1376_214REALME', 15:'1376_214SAMSUNG', 16:'1376_214VERTEX', 17:'1376_214VIVO', 18:'1376_214VSMART', 19:'1376_214XIAOMI', 20:'1376_214ZTE'}
	param_sort = {}
	try:
		param_sort['p_min'] = int(input('Какая минимальная цена телефона? '))
		param_sort['p_max'] = int(input('Какая максимальная цена телефона? '))
		if param_sort['p_max'] == 9999:
			param_sort['p_max'] = 10000
	except ValueError:
		print('Вводите только цифры')
		sorti()
	else:
		print('Доступыне модели телефонов: \n\n0 - Парсить всё')
		for key in models:
			if key == 0:
				continue
			print('{}-{}'.format(key, models[key].replace('1376_214', '')))
		model = int(input('Выберите цифру, с моделью которую хотите парсить (только одну цифру) '))
		param_sort['model'] = models[model]
		return param_sort


def parse():
	# call another function

	html = get_html(URL)
	if html.status_code == 200:
		phones = []
		print('Подготовка к парсингу...')
		param_sort = sorti()
		for page in range(1, PAGES + 1):
			print(f'	Страница {page} обрабатывается, всего {PAGES} страниц...')
			html = get_html(URL, params = {'p' : page, 'f' : param_sort['model'], 'price_min' : param_sort['p_min'], 'price_max' : param_sort['p_max'], 'aviable' : 1})
			phones.extend(get_content(html.text))
		if len(phones) == 0:
			del phones
			print('Ничего не найдено, попробуйте поменять фильтры поиска')
		else:
			print('Запись объектов в csv файл...')
			save_in_file(phones, FILE)
			print(f'Парсинг завершен, найдено {len(phones)} объектов')
			subprocess.call(['libreoffice Citylink.csv'], shell = True)
	else:
		print('Error')

parse()
