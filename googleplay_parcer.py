import requests 
from bs4 import BeautifulSoup 
import argparse
from threading import Thread, Lock
from queue import Queue
import threading
from datetime import datetime


class Scanning(threading.Thread):

    def __init__(self, links):
        self.links = links
        self.count_threads = 20
        self.q = Queue()
        self.print_lock = Lock()
        self.apps = {}

    # Метод с логикой работы
    def link_scan(self, link):
        try:
            # url
            app_url = link

            response = requests.get(link)
            link = BeautifulSoup(response.content, 'html.parser')
            
            # Название
            soup_link = link.find(attrs={"itemprop":"name"})
            app_name = soup_link.text

            # Автор
            app_author = link.title.text[27:]

            # Категория
            app_category = "-"

            # Описание
            soup_link = link.find(attrs={"data-g-id":"description"})
            app_description = '-'
            if soup_link is not None:
                app_description = soup_link.text

            if app_name.find(keyword) == -1 and app_description.find(keyword) == -1:
                return

            # Средняя оценка
            # soup_link = link.find(attrs={"role":"img"})jILTFe
            # app_rate = soup_link.get('aria-label')
            soup_link = link.find(attrs={"class":"jILTFe"})

            app_rate = '-'
            if soup_link is not None:
                app_rate = soup_link.text

            # Кол-во отзывов
            soup_link = link.find(attrs={"class":"EHUI5b"})
            app_count_rate = '-'
            if soup_link is not None:
                app_count_rate = soup_link.text

            # Последнее обновление
            soup_link = link.find(attrs={"class":"xg1aie"})
            app_updated = soup_link.text

            app = {
                'name': app_name,
                'url': app_url,
                'author': app_author,
                'category': app_category,
                'description': app_description,
                'rate': app_rate,
                'count_rate': app_count_rate,
                'updated': app_updated,
                }
            if self.apps.get(app_name) is not None:
                app_name = app_name + '(same)'
            self.apps.update({app_name:app})
        except:
            with self.print_lock:
                print(f"{app_name:40} is scanning", end='\r')
        else:
            with self.print_lock:
                print(f"{app_name:40} has done   ")

    # Метод для работы с каждой задачей
    def scan_thread(self):
        while True:
            # Получение задачи из очереди
            worker = self.q.get()
            self.link_scan(worker)
            # Ответ в очередь, что задача успешно обработана
            self.q.task_done()

    # Основной распределяющий метод
    def main(self):
        for t in range(self.count_threads):
            t = Thread(target=self.scan_thread)
            # Зависимость завершения потока от основного потока
            t.daemon = True
            # Запускаем поток
            t.start()
        for worker in self.links:
            # Каждый элемент помещаем в очередь
            self.q.put(worker)
        # Ожидание завершения потоков
        self.q.join()
        return self.apps


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Host scanner")
    parser.add_argument("--keyword", type=str, help="Keyword, for example: raiffeisen")
    parser.add_argument("--show_mode", default='all', dest="show_mode", type=str, help="How do you want to see results? all-(names,json); names-(only names). Default: all")
    parser.add_argument("--source", default='https://play.google.com', dest="source", type=str, help="The source's link. Default: https://play.google.com")
    parser.add_argument("--lang", default='ru', dest="lang", type=str, help="The source's language. Default: ru")
    parser.add_argument("--country", default='ru', dest="country", type=str, help="The source's country. Default: ru")

    args = parser.parse_args()
    keyword = args.keyword
    show_mode = args.show_mode
    source = args.source
    lang = args.lang
    country = args.country

    locale = f'&hl={lang}&gl={country}'
    response = requests.get(f"{source}/store/search?q={keyword}&c=apps{locale}")
    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.find_all(attrs={"class": "Si6A0c Gy4nib"})
    links = tuple(source + item.get("href") + locale for item in items)

    try:
        time_start = datetime.now()
        scan = Scanning(links)
        results = scan.main()
        if show_mode == 'all':
            print(results)
        time_end = datetime.now()
        print('Results time: ' + str(time_end-time_start))
    except KeyboardInterrupt:
        print('\nScan has been stopped')
