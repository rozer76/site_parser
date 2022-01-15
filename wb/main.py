from parser import goparse

if __name__ == '__main__':
   wb_parser = goparse()
   url = input("Введите URL сайта wildberries.ru:")
   wb_parser.set_url(url)
   wb_parser.run()



