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
			p = item.find('span', class_ = 'subcategory-product-item__price subcategory-product-item__price_standart').get_text(strip = True).replace('\n', '')
			return p
		except AttributeError:
			return 'Уточняйте на сайте'
	else:
		try:
			p_o = item.find('span', class_ = 'subcategory-product-item__price subcategory-product-item__price_old').get_text(strip = True).replace('\n', '')
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
	return phones

def save_in_file(items, path):
	# save info from web-site in csv table

	with open(path, 'w', newline = '') as file:
		writer = csv.writer(file, delimiter = ';')
		writer.writerow(['Название', 'Ссылка', 'Цена со скидкой', 'Цена без скидки'])
		for item in items:
			writer.writerow([item['title'], item['link'], item['price_sale'], item['price_old']])

def parse():
	# call another function

	html = get_html(URL)
	if html.status_code == 200:
		phones = []
		print('Подготовка к парсингу...')
		for page in range(1, PAGES + 1):
			print(f'	Страница {page} обрабатывается, всего {PAGES} страниц...')
			html = get_html(URL, params = {'p' : page})
			phones.extend(get_content(html.text))
		print('Запись объектов в csv файл...')
		save_in_file(phones, FILE)
		print(f'Парсинг завершен, найдено {len(phones)} объектов')
		subprocess.call(['libreoffice Citylink.csv'], shell = True)
	else:
		print('Error')

parse()