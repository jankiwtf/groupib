import argparse
from datetime import datetime
import socket
from threading import Thread, Lock
from queue import Queue
import socket
import threading


class Scanning(threading.Thread):

    def __init__(self, domains):
        self.domains = domains
        self.count_threads = 20
        self.q = Queue()
        self.print_lock = Lock()

    # Метод с логикой работы
    def port_scan(self, domain_name):
        try:
            ip_name = socket.gethostbyname(domain_name)
        except:
            with self.print_lock:
                print(f"{domain_name:20} is scanning       ", end='\r')
        else:
            with self.print_lock:
                if ip_name in ('192.168.1.1','127.0.0.1'):
                    return
                print(f"{domain_name:20}: {ip_name:15}")

    # Метод для работы с каждой задачей
    def scan_thread(self):
        while True:
            # Получение задачи из очереди
            worker = self.q.get()
            self.port_scan(worker)
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
        for worker in self.domains:
            # Каждый элемент помещаем в очередь
            self.q.put(worker)
        # Ожидание завершения потоков
        self.q.join()


# Добавление символа
def char_add(word):
    chars = ['a', 'b', 'c', 'd', 'e', 'f', 'j', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v','w', 'x', 'y', 'z']
    keywords = tuple(word + char for char in chars)
    return set(keywords)

# Подстановка похожего символа
def char_replace(word):
    homoglyphs = {
    'o':'0',
    'O':'0',
    'l':'1',
    'i':'1',
    'd':'cl',
    'w':'vv'
    }
    keywords = list()
    for char in enumerate(word):
        chars = list(word)
        homoglyph = homoglyphs.get(char[1])
        if homoglyph is not None:
            chars[char[0]] = homoglyph
            new_word = ''.join(chars)
            keywords.append(new_word)
            result = char_replace(new_word)
            keywords.extend(result)
    return set(keywords)

# Выделение поддомена
def under_domain(word):
    keywords = list()
    for char in enumerate(word[1:],1):
        chars = list(word)
        # print(char)
        if word[char[0]-1] == '-' or char[1] == '-':
            continue
        new_char = '.' + char[1]
        chars[char[0]] = new_char
        keywords.append(''.join(chars))
    return set(keywords)

# Удаление символа
def char_delete(word):
    keywords = list()
    for char in range(len(word)):
        chars = list(word)
        chars[char] = ''
        keywords.append(''.join(chars))
    return set(keywords)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Host scanner")
    parser.add_argument("--keyword", type=str, help="Keyword, for example: group-ib")
    parser.add_argument("--domains_zone", default='com,ru,net,org,info,cn,es,top,au,pl,it,uk,tk,ml,ga,cf,us,xyz,top,site,win,bid', dest="domains_zone", type=str, help="Domains zone to scan, without spaces. Default: com,ru,net,org,info,cn,es,top,au,pl,it,uk,tk,ml,ga,cf,us,xyz,top,site,win,bid")

    args = parser.parse_args()
    keyword = args.keyword
    domains_zone = args.domains_zone.split(',')

    keywords = {keyword}
    keywords.update(char_add(keyword))
    keywords.update(char_replace(keyword))
    keywords.update(under_domain(keyword))
    keywords.update(char_delete(keyword))

    domains = set()
    domains_name = list( domains.update(set(keyword + '.' + domain for domain in domains_zone)) for keyword in keywords )

    try:
        time_start = datetime.now()
        scan = Scanning(domains)
        scan.main()
        time_end = datetime.now()
        print('Results time: ' + str(time_end-time_start))
    except KeyboardInterrupt:
        print('\nScan has been stopped')
