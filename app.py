import asyncio

import serial.tools.list_ports


async def find_ports():
    """ Определяет список COM-портов или выводит инфо об ошибке их поиска """
    while True:
        print("Поиск COM-портов...")
        ports = serial.tools.list_ports.comports()
        # sorted_ports = sorted(list(map(lambda port: port.name, ports)))
        sorted_ports = ["COM1", "COM2", "COM3"]
        count = len(sorted_ports)
        print(f"Найдено портов: {count}")
        if count > 0:
            return dict(zip([i for i in range(3)], sorted_ports))
            # return list(zip(sorted_ports, [i for i in range(count)]))
        await asyncio.sleep(3)


async def select_port(ports):
    while True:
        for key, value in ports.items():
            print(f"{key}. {value}")
        port_num = int(input("Выберите порт: "))
        if port_num in ports.keys():
            return ports.get(port_num)


async def run():
    ports = await find_ports()
    bemp_port = await select_port(ports)


    print(bemp_port)
