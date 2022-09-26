import pygame

import voicing
from bemp import Bemp
from connect import get_mb_client
from polling import run_polling


def run():
    pygame.init()
    bemp = Bemp()
    mb_client = get_mb_client(bemp)
    speaker, di_off_voicing = voicing.configure_voicing()
    run_polling(bemp, mb_client, speaker, di_off_voicing)
