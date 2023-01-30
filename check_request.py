from textwrap import dedent

import requests
from loguru import logger
from environs import Env
import telegram

import time
from datetime import datetime

from telegram import ParseMode


def retry_request(func):
    def wrapper(*args, **kwargs):
        reconnect_time = 0.1
        while True:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.ConnectionError:
                time.sleep(reconnect_time)
                reconnect_time *= 2
                logger.warning(f'Потеря соединения. Повторный запрос через {reconnect_time} секунд')

    return wrapper


@retry_request
def get_response(url: str, headers: dict = None, timeout: int = None) -> requests.Response:
    response: requests.Response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response


def create_telegram_message(response_json: dict) -> str:
    new_attempts = response_json['new_attempts'][0]
    is_negative = 'Работа возвращена' if new_attempts['is_negative'] is True else 'Работа проверена'
    answer = dedent(f"""
    <b>{new_attempts['lesson_title']}</b>
    
    {is_negative}
    {new_attempts['lesson_url']}
    """)

    return answer


def get_list_of_checks(devman_api_token: str, bot: telegram.Bot, chat_id: int, timeout: int = 300) -> None:
    timestamp = datetime.now().timestamp()
    logger.debug(f'TIMESTAMP_NOW: {timestamp}')

    headers = {
        'Authorization': f'Token {devman_api_token}'
    }
    while True:
        url = f'https://dvmn.org/api/long_polling/?timestamp={timestamp}'
        logger.debug(url)
        logger.info(f'Запустили LONG POLLING. Таймаут {timeout} секунд')
        try:
            response = get_response(url, headers=headers, timeout=timeout)
            response_json = response.json()
            if response_json.get('status') == 'found':
                telegram_message = create_telegram_message(response_json)
                bot.send_message(chat_id=chat_id, text=telegram_message, parse_mode=ParseMode.HTML)

            timestamp = response_json.get('timestamp_to_request') or response_json.get('last_attempt_timestamp')
            logger.info(response.json())

        except requests.exceptions.ReadTimeout as error:
            logger.warning(f'Таймаут запроса отработал раньше чем сервер ответил: {error}')
            timestamp = datetime.now().timestamp()
            continue


def main():
    env = Env()
    env.read_env()

    devman_api_token = env("DEVMAN_TOKEN_API")
    telegram_api_key = env("TELEGRAM_API_KEY")
    telegram_chat_id = env("TELEGRAM_CHAT_ID")

    bot = telegram.Bot(token=telegram_api_key)

    logger_level = "DEBUG" if env('DEBUG_MODE', False) else "INFO"
    logger.add('logging.log', format="{time} {level} {message}", level=logger_level)

    get_list_of_checks(devman_api_token, bot, telegram_chat_id)


if __name__ == '__main__':
    main()
