import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


class TgBotError(Exception):
    """Собственный класс ошибки."""

    pass


def log_and_raise_error(error_msg):
    """Логирование и возбуждение исключения."""
    message = f'Сбой в работе: {error_msg}'
    logger.error(message)
    raise TgBotError(message)


def send_message(bot, message):
    """Сообщение от бота."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


class EndpointError(Exception):
    """Собственный класс ошибки."""

    pass


def get_api_answer(current_timestamp):
    """Получаем ответ API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homeworks = requests.get(
            ENDPOINT, headers=HEADERS,
            params=params
        )
    except requests.exceptions.HTTPError as error:
        message = f'Другая ошибка {error}'
        logger.error(message)
        raise ValueError(message)
    if homeworks.status_code != HTTPStatus.OK:
        raise EndpointError(
            f'Сбой в работе программы: Эндпоинт {ENDPOINT} не доступен.'
            f'Код ответа API {homeworks.status_code}'
        )
    return homeworks.json()


def check_response(response):
    """Проверяет ответ."""
    homeworks_key = 'homeworks'
    try:
        homeworks = response[homeworks_key]
        time_stamp = response['current_date']
    except KeyError as error:
        error_msg = f'Ключ {error} отсутствует в ответе API'
        log_and_raise_error(error_msg)
    else:
        if not isinstance(homeworks, list):
            error_msg = (
                f'Под ключом {homeworks_key} в ответе API '
                f'содержится некорректный тип: {type(homeworks)}'
            )
            log_and_raise_error(error_msg)
        if not homeworks:
            logger.debug(
                (
                    'Статус домашних работ не изменился '
                    f'с отметки UNIX-time: {time_stamp}'
                )
            )
        return homeworks


def parse_status(homework):
    """Возвращает вердикт о статусе домашней работы."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except KeyError:
        raise KeyError('Статус работы не документирован')
    verdict = HOMEWORK_STATUSES[homework_status]
    return (
        'Изменился статус проверки работы '
        f'"{homework_name}". {verdict}'
    )


def check_tokens():
    """Проверяет токены."""
    env_data = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    }

    for token_name, token_value in env_data.items():
        if not token_value:
            logger.critical(
                f'Отсутствует переменная: {token_name}'
            )
            return False
    return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        return
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homewrks = check_response(response)
            current_timestamp = response['current_date']
            for homework in homewrks:
                verdict = parse_status(homework)
                send_message(bot, verdict)

        except Exception as error:
            message = f'Сбой в работе: {error}'
            logger.error(message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
