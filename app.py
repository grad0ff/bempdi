import os
import sys
import time
from threading import Thread

import pygame
import serial.tools.list_ports
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.exceptions import ConnectionException

from bemp import Bemp


def find_ports():
    """Возвращает перечень COM-портов в виде словаря"""
    while True:
        print("Поиск COM-портов...")
        ports = serial.tools.list_ports.comports()
        sorted_ports = sorted(list(map(lambda port: port.name, ports)))
        count = len(sorted_ports)
        if count > 0:
            print(f"Найдено портов: {count}")
            return dict(zip([i for i in range(count)], sorted_ports))
        time.sleep(3)
        print("COM-порты не найдены...")


def select_port(ports):
    """Возвращает имя выбранного COM-порта"""
    while True:
        for key, value in ports.items():
            print(f"{key} - {value}")
        port = input(f"Введите число, соответствующее COM-порту БЭМП: ")
        if port.isnumeric() and int(port) in range(len(ports)):
            bemp_port = ports.get(int(port))
            print(f"Выбран порт: {bemp_port}")
            return bemp_port


def get_mb_client(port):
    """ Подключает к устройству, возвращает Modbus клиент """
    print(f'Проверка связи с БЭМП...')
    try:
        client = ModbusSerialClient(
            method=Bemp.method,
            port=port,
            baudrate=Bemp.speed,
            bytesize=Bemp.bytesize,
            parity=Bemp.parity,
            stopbits=Bemp.stopbits)
        client.connect()
        if client.socket is None:
            raise ConnectionException
        elif client.is_socket_open():
            print("Устройство подключено")
            return client
    except ConnectionException:
        print(f"Ошибка подключения. Возможно, порт {port} занят или недоступен. Выход из программы")
        exit(1)
    except Exception as e:
        print(f"Exception: {e}")


def run_polling(mb_client, off_state_voicing):
    Bemp.di_count = get_di_count(mb_client)
    di_status_list_old = [False for _ in range(Bemp.di_count)]
    di_status_list_new = []

    while True:
        print("listen")
        try:
            di_status_list_new = mb_client.read_coils(Bemp.di_start_address, Bemp.di_count, unit=Bemp.address).bits
        except Exception as e:
            print(f"Exception: {e}")

        for i in range(Bemp.di_count):
            if di_status_list_new[i] != di_status_list_old[i]:
                if di_status_list_new[i] or (not di_status_list_new[i] and off_state_voicing):
                    di_num = i + 1
                    try:
                        print(f"ДВ {di_num} - on")
                        di_song = pygame.mixer.Sound(resource_path(f"resources/songs/Daria/di/{di_num}.wav"))
                        song_time = di_song.get_length() - 0.3
                        di_song.play()
                        time.sleep(song_time)

                        if not di_status_list_new[i]:
                            print(f"ДВ {di_num} - off")
                            song_dio_state = pygame.mixer.Sound(
                                resource_path(f"resources/songs/Daria/on-off/отключено.wav"))
                            song_time = song_dio_state.get_length() - 0.1
                            song_dio_state.play()
                            time.sleep(song_time)
                    except Exception as e:
                        print(f"Exception: {e}")
        di_status_list_old = di_status_list_new.copy()
        time.sleep(0.5)


def get_di_count(mb_client):
    print("Чтение количества ДВ в БЭМП...")
    try:
        di_count = mb_client.read_holding_registers(Bemp.di_count_address, unit=Bemp.address).registers[0]
    except Exception as e:
        print(f"Exception: {e}")
    else:
        print(f"Количество ДВ: {di_count}")
        return di_count


def check_connect(mb_client):
    """Проверяет статус подключения к устройству"""
    while True:
        print("check")
        if not mb_client.is_socket_open():
            print("Соединение c устройством потеряно... Выход из программы")
        time.sleep(1)


def get_off_state_voicing():
    """Возвращает флаг озвучивания при отключении ДВ"""
    while True:
        off_state_voicing = input("Озвучивать отключение ДВ? [1-Да / 0-Нет] ")
        if off_state_voicing.isnumeric():
            num = int(off_state_voicing)
            if num in [0, 1]:
                return bool(num)


def resource_path(relative_path):
    """Возвращает путь для добавляемых в *.exe ресурсов (иконки, звуки и т.п.)"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def run():
    pygame.init()
    ports = find_ports()
    bemp_port = select_port(ports)
    mb_client = get_mb_client(bemp_port)
    off_state_voicing = get_off_state_voicing()
    tread1 = Thread(target=check_connect, args=(mb_client,), name="check_connect_thread")
    tread2 = Thread(target=run_polling, args=(mb_client, off_state_voicing), name="polling_thread")
    tread1.start()
    tread2.start()
    tread1.join()
    tread2.join()
    # run_polling(mb_client, off_state_voicing)
