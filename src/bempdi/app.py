import os
import time

import pygame

from src.bempdi import voicing
from src.bempdi.bemp import Bemp
from src.bempdi.connect import get_mb_client
from src.bempdi.log_manage import logger
from src.bempdi.polling import run_polling


def run():
    try:
        pygame.init()
        os.system("cls")  # очистка консоли от вывода pygame
        bemp = Bemp()
        mb_client = get_mb_client(bemp)
        speaker, di_off_voicing = voicing.configure_voicing()
        run_polling(bemp, mb_client, speaker, di_off_voicing)
    except BaseException as e:
        logger.error(e)
        time.sleep(5)
        exit(1)
