import asyncio
import os
import sys
import time

import pygame
import serial.tools.list_ports
from pymodbus.client.sync import ModbusSerialClient

from bemp import Bemp


async def find_ports():
    """ Определяет список COM-портов или выводит инфо об ошибке их поиска """
    while True:
        print("Поиск COM-портов...")
        ports = serial.tools.list_ports.comports()
        sorted_ports = sorted(list(map(lambda port: port.name, ports)))
        # sorted_ports = ["COM1", "COM2", "COM3"]
        count = len(sorted_ports)
        print(f"Найдено портов: {count}")
        if count > 0:
            # return dict(zip([i for i in range(3)], sorted_ports))
            return dict(zip([i for i in range(count)], sorted_ports))
        await asyncio.sleep(3)


async def select_port(ports):
    while True:
        for key, value in ports.items():
            print(f"{key}. {value}")

        port = input("Выберите порт: ")
        if port.isnumeric() and int(port) in range(len(ports)):
            return ports.get(int(port))


async def get_client(port) -> ModbusSerialClient:
    """ Проверяет связь с устройством, возвращает модбас клиент """
    print(f'Проверка связи с БЭМП...')
    try:
        client = ModbusSerialClient(
            method=Bemp.method,
            port=port,
            baudrate=Bemp.speed,
            bytesize=Bemp.bytesize,
            parity=Bemp.parity,
            stopbits=Bemp.stopbits)
        if client.connect() and client.is_socket_open():
            print("Устройство подключено")
            return client
    except Exception as e:
        print(f"Exeption: {e}")


async def get_di_count(mb_client):
    print("Чтение количества ДВ")
    try:
        Bemp.di_count = mb_client.read_holding_registers(0x0100, unit=Bemp.address).registers[0]
        print(f"Количество ДВ: {Bemp.di_count}")
    except Exception as e:
        print(f"Exeption: {e}")


async def run_polling(mb_client, off_state_voicing):
    di_status_list_old = [False for i in range(Bemp.di_count)]
    di_status_list_new = []

    while True:
        try:
            di_status_list_new = mb_client.read_coils(Bemp.di_start_address, Bemp.di_count, unit=Bemp.address).bits
        except Exception as e:
            print(f"Exeption: {e}")

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
                        print(f"Exeption: {e}")

        di_status_list_old = di_status_list_new.copy()
        await asyncio.sleep(1)


async def get_off_state_voicing():
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


async def run():
    pygame.init()
    ports = await find_ports()
    bemp_port = await select_port(ports)
    mb_client = await get_client(bemp_port)
    await get_di_count(mb_client)
    off_state_voicing = await get_off_state_voicing()
    await run_polling(mb_client, off_state_voicing)
