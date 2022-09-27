import os
import sys
import time
from threading import Thread

import pygame


def polling(device, mb_client, speaker, is_di_off_voicing):
    """Обеспечивает опрос ДВ устройства"""
    state_list_old = [False for _ in range(device.di_count)]
    state_list_new = []
    is_first_request = True
    print("\nОпрос ДВ...")

    while True:
        try:
            state_list_new = mb_client.read_coils(device.di_start_address, device.di_count, unit=device.address).bits
        except Exception as e:
            print(f"Exception: {e}")
        for i in range(device.di_count):
            # если состояние ДВ изменилось
            if not is_first_request and state_list_new[i] != state_list_old[i]:
                di_num = i + 1
                try:
                    # если ДВ сработал или флаг озвучки отключения True
                    if state_list_new[i] or is_di_off_voicing:
                        di_song = pygame.mixer.Sound(resource_path(f"resources/songs/{speaker}/di/{di_num}.wav"))
                        song_time = di_song.get_length() - 0.2
                        di_song.play()
                        time.sleep(song_time)
                        if state_list_new[i]:
                            print(f"ДВ {di_num} - on")
                        else:
                            print(f"ДВ {di_num} - off")
                            if is_di_off_voicing:
                                di_song = pygame.mixer.Sound(resource_path(f"resources/songs/{speaker}/on-off/off.wav"))
                                song_time = di_song.get_length() - 0.1
                                di_song.play()
                                time.sleep(song_time)
                except Exception as e:
                    print(f"Exception: {e}")
        state_list_old = state_list_new.copy()
        is_first_request = False
        time.sleep(0.5)


def get_di_count(device, mb_client):
    """Возвращает количество ДВ в БЭМП"""
    try:
        di_count = mb_client.read_holding_registers(device.di_count_address, unit=device.address).registers[0]
    except Exception as e:
        print(f"Exception: {e}")
    else:
        return di_count


def check_connect(mb_client):
    """Проверяет статус подключения к устройству"""
    while True:
        if not mb_client.is_socket_open():
            print("Соединение c устройством потеряно... Выход из программы")
            exit(1)
        time.sleep(0.25)


def resource_path(relative_path):
    """Возвращает путь для добавляемых в *.exe ресурсов (иконки, звуки и т.п.)"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def run_polling(device, mb_client, speaker, di_off_voicing):
    device.di_count = get_di_count(device, mb_client)
    thread1 = Thread(target=polling, args=(device, mb_client, speaker, di_off_voicing), name="polling_thread")
    thread1.setDaemon(True)
    thread1.start()
    check_connect(mb_client)
    thread1.join()
