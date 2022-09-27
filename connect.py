import sys
import time

import serial.tools.list_ports
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.exceptions import ConnectionException


def find_ports():
    """Возвращает перечень COM-портов в виде словаря"""
    while True:
        print("Поиск COM-портов...")
        ports = serial.tools.list_ports.comports()
        sorted_ports = sorted(list(map(lambda port: port.name, ports)))
        count = len(sorted_ports)
        if count > 0:
            print(f"Найдено портов: {count}\n")
            return dict(zip([i for i in range(count)], sorted_ports))
        time.sleep(3)
        print("COM-порты не найдены...")


def select_port(ports):
    """Возвращает имя выбранного COM-порта"""
    while True:
        for key, value in ports.items():
            print(f"{key} - {value}")
        port = input(f"Введите число, соответствующее COM-порту БЭМП [0-{len(ports)}]: ")
        if port.isnumeric() and int(port) in range(len(ports)):
            bemp_port = ports.get(int(port))
            print(f"Выбран порт: {bemp_port}\n")
            return bemp_port


def get_connect(device, port):
    """Подключает к устройству, возвращает Modbus клиент"""
    print(f'Проверка связи с БЭМП...')
    try:
        client = ModbusSerialClient(
            method=device.method,
            port=port,
            baudrate=device.speed,
            bytesize=device.bytesize,
            parity=device.parity,
            stopbits=device.stopbits)
        client.connect()
        if client.socket is None or not client.is_socket_open():
            raise ConnectionException
    except ConnectionException:
        print(f"Ошибка подключения. Возможно, порт {port} занят или недоступен.\n"
              f"Выход из программы...")
        time.sleep(2)
        sys.exit(1)
    except Exception as e:
        print(f"Exception: {e}")
    else:
        print("Устройство подключено\n")
        return client


def get_mb_client(device):
    ports = find_ports()
    bemp_port = select_port(ports)
    mb_client = get_connect(device, bemp_port)
    return mb_client
