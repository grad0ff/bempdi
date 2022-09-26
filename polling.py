import os
import sys
import time
from threading import Thread

import pygame


def polling(device, mb_client, speaker, off_state_voicing):
    device.di_count = get_di_count(device, mb_client)
    di_status_list_old = [False for _ in range(device.di_count)]
    di_status_list_new = []

    while True:
        try:
            di_status_list_new = mb_client.read_coils(device.di_start_address, device.di_count,
                                                      unit=device.address).bits
        except Exception as e:
            print(f"Exception: {e}")

        for i in range(device.di_count):
            if di_status_list_new[i] != di_status_list_old[i]:
                if di_status_list_new[i] or (not di_status_list_new[i] and off_state_voicing):
                    di_num = i + 1
                    try:
                        print(f"ДВ {di_num} - on")
                        di_song = pygame.mixer.Sound(resource_path(f"resources/songs/{speaker}/di/{di_num}.wav"))
                        song_time = di_song.get_length() - 0.2
                        di_song.play()
                        time.sleep(song_time)

                        if not di_status_list_new[i]:
                            print(f"ДВ {di_num} - off")
                            song_dio_state = pygame.mixer.Sound(
                                resource_path(f"resources/songs/{speaker}/on-off/off.wav"))
                            song_time = song_dio_state.get_length() - 0.1
                            song_dio_state.play()
                            time.sleep(song_time)
                    except Exception as e:
                        print(f"Exception: {e}")
        di_status_list_old = di_status_list_new.copy()
        time.sleep(0.5)


def get_di_count(device, mb_client):
    print("Чтение количества ДВ в БЭМП...")
    try:
        di_count = mb_client.read_holding_registers(device.di_count_address, unit=device.address).registers[0]
    except Exception as e:
        print(f"Exception: {e}")
    else:
        print(f"Количество ДВ: {di_count}")
        return di_count


def check_connect(mb_client):
    """Проверяет статус подключения к устройству"""
    while True:
        if not mb_client.is_socket_open():
            print("Соединение c устройством потеряно... Выход из программы")
            exit(1)
        time.sleep(0.5)


def resource_path(relative_path):
    """Возвращает путь для добавляемых в *.exe ресурсов (иконки, звуки и т.п.)"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def run_polling(device, mb_client, speaker, di_off_voicing):
    thread1 = Thread(target=polling, args=(device, mb_client, speaker, di_off_voicing), name="polling_thread")
    thread1.setDaemon(True)
    thread1.start()
    check_connect(mb_client)
    thread1.join()
