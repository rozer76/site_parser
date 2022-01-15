import requests
import logging
import collections
import bs4
import csv


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wb')

ParseResult = collections.namedtuple('ParseResult',
                                     ('goods',
                                      'url',
                                      'brand',
                                      'price'))
HEADERS = ('Товар',
            'Ссылка',
            'Бренд',
            'Цена')


class goparse:

    ROOT_SITE = 'https://www.wildberries.ru'
    URL = None

    def __init__(self):
        self.session = requests.session()
        self.session.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
                                'Accept-Language':'ru'}
        self.result = []
        self.max_page = 0
        self.qty_pages = 0

    def set_url(self, url: str):
        self.URL = url

    def load_page(self, page: int = 0):
        url = self.URL
        if page != 0:
            res = self.session.get(url, params={'page': page})
        else:
            res = self.session.get(url)
        res.raise_for_status()
        return res.text

    def parse_page(self, text: str):
        soup = bs4.BeautifulSoup(text, "html.parser")
        container = soup.select('div.product-card.j-card-item')
        for block in container:
            self.parse_block(block)

    def parse_block(self, block):
        #logger.debug(block)
        #logger.debug('=' * 100)

        #url
        url_block = block.select_one('a.product-card__main.j-open-full-product-card')
        if not url_block:
            logger.error('Нет блока ссылки на товар')
            return
        url = url_block.get('href')
        if not url:
            logger.error('Нет ссылки на товар')
            return
        url = self.ROOT_SITE + url

        #goods
        goods_block = block.select_one('span.goods-name')
        if not goods_block:
            logger.error(f'Нет наименования товара для {url}')
            return
        goods = goods_block.text
        goods = goods.strip()

        #brand
        brand_block = block.select_one('strong.brand-name')
        if not brand_block:
            logger.error(f'Нет бренда для товара для {url}')
            return
        brand = brand_block.text
        brand = brand.replace('/','').strip()

        #price
        price_block1 = block.select_one('ins.lower-price')
        price_block2 = block.select_one('span.lower-price')
        if price_block1 != None:
            price = price_block1.text
        elif price_block2 != None:
            price = price_block2.text
        else:
            price = 'цену уточняйте'

        logger.debug('%s | %s | %s | %s', url, goods, brand, price)

        self.result.append(ParseResult(goods=goods,url=url,brand=brand, price=price))

    def run(self):
        url = self.URL
        try:
            res = self.session.get(url)
        except:
            logger.info(f'Ошибка URL')
            return
        try:
            res.raise_for_status()
            self.pagination_info(res)
            for page in range(self.qty_pages + 1):
                logger.info(f'Страница {page} из {self.qty_pages}')
                text = self.load_page(page=page)
                self.parse_page(text)
            logger.info(f'Получили {len(self.result)} элементов и  записали в \"res.csv\"')
        except:
            logger.info(f'Ошибка парсинга')
            return
        try:
            self.save_results()
        except:
            logger.info(f'Ошибка записи в файл \"res.csv\"')
            return

    def save_results(self):
        with open('res.csv','w',encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(HEADERS)
            for res in self.result:
                writer.writerow(res)

    def pagination_info(self, res):
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        find_pagination_item = soup.find_all('a', class_='pagination-item')
        if find_pagination_item:
            self.qty_pages = int(find_pagination_item[-1].text)
            if self.max_page == self.qty_pages or self.max_page > self.qty_pages:
                logger.info(f'Всего найдего страниц пагинации {self.qty_pages}')
                return
            self.max_page = self.qty_pages
            logger.info(f'Анализ страниц пагинации {self.qty_pages}')
            url = self.URL
            res = self.session.get(url, params={'page': self.qty_pages + 1})
            res.raise_for_status()
            self.pagination_info(res)
        else:
            return

if __name__ == '__main__':
   myParser = goparse()
   myParser.run()






