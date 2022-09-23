import serial.tools.list_ports


def find_ports():
    """ Определяет список COM-портов или выводит инфо об ошибке их поиска """
    print("Поиск COM-портов...")
    ports = []
    all_ports = serial.tools.list_ports.comports()  # получить список активных COM-портов
    ports = sorted(list(map(lambda port: port.name, all_ports)))
    print(all_ports)
    # self.send_to_statusbar(f'Поиск завершен. Найдено COM-портов:  {len(ports)}')
    # if not ports:
    #     ports.append()


find_ports()
