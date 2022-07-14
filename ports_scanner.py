import argparse
from datetime import datetime
import socket
from threading import Thread, Lock
from queue import Queue
import threading
import requests


class Scanning(threading.Thread):

    def __init__(self, host, ports):
        self.host = host
        self.ports = ports
        self.count_threads = 20
        self.q = Queue()
        self.print_lock = Lock()

    # Метод с логикой работы
    def port_scan(self, port):
        try:
            s = socket.socket()
            s.settimeout(1)
            s.connect((self.host, port))
        except:
            with self.print_lock:
                print(f"{self.host:14}:{port:5} is scanning", end='\r')
        else:
            with self.print_lock:
                print(f"{self.host:14}:{port:5} is open    ")
                if port == 80 or port == 443:
                    try:                        
                        url = f"http://{self.host}:{port}"
                        response = requests.head(url)
                        print('Server:', response.headers.get('Server'))
                    except Exception as error:
                        print(error)
        finally:
            s.close()

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
        for worker in self.ports:
            # Каждый элемент помещаем в очередь
            self.q.put(worker)
        # Ожидание завершения потоков
        self.q.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Host scanner")
    parser.add_argument("--hosts", type=str, help="Hosts to scan, one or many. Example: 192.168.1.0/24 or 192.168.1.5/12")
    parser.add_argument("--ports", type=str, help="Ports to scan, without spaces. Example: 80,443,22,21000,25000")
    args = parser.parse_args()
    hosts = args.hosts.split('.')
    main_host = '.'.join(hosts[:-1])
    start_host = int(hosts[-1].split("/")[0])
    end_host = int(hosts[-1].split("/")[1]) + 1
    hosts = [f'{main_host}.{str(host)}' for host in range(start_host, end_host)]
    ports = args.ports
    ports = [int(port) for port in ports.split(",")]

    try:
        time_start = datetime.now()
        for host in hosts:
            scan = Scanning(host, ports)
            scan.main()
        time_end = datetime.now()
        print('Results time: ' + str(time_end-time_start))
    except KeyboardInterrupt:
        print('\nScan has been stopped')
