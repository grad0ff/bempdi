speakers = {0: "Daria", 1: "Maksim"}


def select_speaker():
    """Возвращает имя выбранного диктора"""
    while True:
        for key, value in speakers.items():
            print(f"{key} - {value}")
        speaker_num = input(f"Введите число, соответствующее спикеру [0-{len(speakers) - 1}]: ")
        if speaker_num.isnumeric() and int(speaker_num) in speakers.keys():
            speaker_num = speakers.get(int(speaker_num))
            print(f"Выбран спикер: {speaker_num}\n")

            return speaker_num


def get_off_state_voicing():
    """Возвращает флаг озвучивания при отключении ДВ"""
    while True:
        off_state_voicing = input("Озвучивать отключение ДВ? [1-Да / 0-Нет] ")
        if off_state_voicing.isnumeric():
            num = int(off_state_voicing)
            if num in [0, 1]:
                return bool(num)


def configure_voicing():
    speaker = select_speaker().lower()
    di_off_voicing = get_off_state_voicing()
    return speaker, di_off_voicing
