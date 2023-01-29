import sys

import requests  # type: ignore
from loguru import logger
from environs import Env


def get_list_of_checks(devman_api_token: str) -> dict:
    url = 'https://dvmn.org/api/user_reviews/'
    headers = {
        'Authorization': f'Token {devman_api_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


def main():
    env = Env()
    env.read_env()

    devman_api_token = env("DEVMAN_TOKEN_API")

    logger_level = "DEBUG" if env('DEBUG_MODE', False) else "INFO"
    logger.add(sys.stderr, format="{time} {level} {message}", level=logger_level)

    list_of_checks = get_list_of_checks(devman_api_token)


if __name__ == '__main__':
    main()
