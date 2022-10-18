import logging
import os
import sys
from logging import Logger


class LogManager:
    __logger: Logger
    _log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"

    def __init__(self, logger_name, level):
        self.__logger = logging.getLogger(logger_name)
        self.__logger.setLevel(level)

    def add_stream_handler(self, level=logging.INFO):
        self.__logger.addHandler(self.__get_stream_handler(level))

    def __get_stream_handler(self, level):
        """
        Возвращает обработчик потока вывода в консоль
        """
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(logging.Formatter(self._log_format))
        stream_handler.setStream(sys.stdout)

        return stream_handler

    def add_file_handler(self, logs_dir, file_name, level=logging.INFO):
        self.__logger.addHandler(self.__get_file_handler(level, logs_dir, file_name))

    def __get_file_handler(self, level, logs_dir, file):
        """
        Возвращает обработчик потока вывода в файл
        """
        dir_abs_path = os.path.abspath(logs_dir)
        if not os.path.exists(dir_abs_path):
            os.mkdir(dir_abs_path)
        file_path = logs_dir + "/" + file
        file_handler = logging.FileHandler(filename=file_path, mode="w")
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(self._log_format))

        return file_handler

    def get_logger(self):
        return self.__logger


log_manager = LogManager(__name__, logging.DEBUG)
log_manager.add_file_handler("C:/bempdi_logs", "log.txt", logging.DEBUG)
logger = log_manager.get_logger()
