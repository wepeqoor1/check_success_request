import sys
import time
from datetime import datetime
from textwrap import dedent

import requests
import telegram
from environs import Env
from loguru import logger
from telegram import ParseMode

import emojy


def send_telegram_message(response_json: dict, chat_id: int, bot: telegram.Bot) -> None:
    new_attempts = response_json['new_attempts'][0]
    is_negative = f'{emojy.false}Работа не выполнена{emojy.false}' \
        if new_attempts['is_negative'] is True \
        else f'{emojy.true}Работа сдана{emojy.true}'

    telegram_message = dedent(f"""
    {emojy.ufo}<b>{new_attempts['lesson_title']}</b>{emojy.ufo}

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

    reconnect_time = 0.1

    while True:
        url = f'https://dvmn.org/api/long_polling/'
        logger.info(f'Запустили LONG POLLING. Таймаут {timeout} секунд')
        try:
            # Делаем запрос к API
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            response.raise_for_status()

            checked_tasks = response.json()
            logger.debug(checked_tasks)
            # Если запрос верный - отправляем сообщение в Телеграм
            if checked_tasks.get('status') == 'found':
                send_telegram_message(checked_tasks, chat_id, bot)

            timestamp = checked_tasks.get('timestamp_to_request') or checked_tasks.get('last_attempt_timestamp')
            params = {'timestamp': timestamp}
            reconnect_time = 0.1
            logger.info(checked_tasks)

        except requests.exceptions.ReadTimeout as error:
            logger.warning(f'Таймаут запроса отработал раньше чем сервер ответил: {error}')
            timestamp = datetime.now().timestamp()
            params = {'timestamp': timestamp}
            continue

        except requests.exceptions.ConnectionError:
            time.sleep(reconnect_time)
            reconnect_time *= 2
            logger.warning(f'Потеря соединения. Повторный запрос через {reconnect_time} секунд')


def main():
    env = Env()
    env.read_env()

    devman_api_token = env('DEVMAN_TOKEN_API')
    telegram_api_key = env('TELEGRAM_API_KEY')
    telegram_chat_id = env('TELEGRAM_CHAT_ID')

    bot = telegram.Bot(token=telegram_api_key)

    logger_level = 'DEBUG' if env('DEBUG_MODE', False) else 'INFO'
    logger.add(sys.stdout, format='{time} {level} {message}', level=logger_level)

    get_new_checks(devman_api_token, bot, telegram_chat_id)


if __name__ == '__main__':
    main()
