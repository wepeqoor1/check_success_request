import time
from datetime import datetime
from textwrap import dedent

import requests
import telegram
from environs import Env
from loguru import logger
from telegram import ParseMode


def get_response(url: str, headers: dict = None, params: dict = None, timeout: int = None) -> requests.Response:
    reconnect_time = 0.1
    while True:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.ConnectionError:
            time.sleep(reconnect_time)
            reconnect_time *= 2
            logger.warning(f'Потеря соединения. Повторный запрос через {reconnect_time} секунд')


def send_telegram_message(response_json: dict, chat_id: int, bot: telegram.Bot) -> None:
    new_attempts = response_json['new_attempts'][0]
    is_negative = 'Работа не выполнена' if new_attempts['is_negative'] is True else 'Работа сдана'

    telegram_message = dedent(f"""
    <b>{new_attempts['lesson_title']}</b>

    {is_negative}
    {new_attempts['lesson_url']}
    """)

    bot.send_message(chat_id=chat_id, text=telegram_message, parse_mode=ParseMode.HTML)
    logger.debug('Сообщение отправлено в чат Телеграмма')


def get_new_checks(devman_api_token: str, bot: telegram.Bot, chat_id: int, timeout: int = 300) -> None:
    timestamp = datetime.now().timestamp()
    logger.debug(f'TIMESTAMP_NOW: {timestamp}')

    headers = {'Authorization': f'Token {devman_api_token}'}
    params = {'timestamp': timestamp}

    while True:
        url = f'https://dvmn.org/api/long_polling/'
        logger.info(f'Запустили LONG POLLING. Таймаут {timeout} секунд')
        try:
            # Делаем запрос к API
            response = get_response(url, headers=headers, params=params, timeout=timeout)
            response_api = response.json()
            logger.debug(response_api)
            # Если запрос верный - отправляем сообщение в Телеграм
            if response_api.get('status') == 'found':
                send_telegram_message(response_api, chat_id, bot)

            timestamp = response_api.get('timestamp_to_request') or response_api.get('last_attempt_timestamp')
            params = {'timestamp': timestamp}
            logger.info(response_api)

        except requests.exceptions.ReadTimeout as error:
            logger.warning(f'Таймаут запроса отработал раньше чем сервер ответил: {error}')
            timestamp = datetime.now().timestamp()
            params = {'timestamp': timestamp}

            continue


def main():
    env = Env()
    env.read_env()

    devman_api_token = env('DEVMAN_TOKEN_API')
    telegram_api_key = env('TELEGRAM_API_KEY')
    telegram_chat_id = env('TELEGRAM_CHAT_ID')

    bot = telegram.Bot(token=telegram_api_key)

    logger_level = 'DEBUG' if env('DEBUG_MODE', False) else 'INFO'
    logger.add('logging.log', format='{time} {level} {message}', level=logger_level)

    get_new_checks(devman_api_token, bot, telegram_chat_id)


if __name__ == '__main__':
    main()
