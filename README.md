# CHECK SUCCESS REQUEST
Проверка статуса работ на devman.org

## Описание
Скрипт предназначен для получения информации о выполненных работах с сайта https://dvmn.org/api/docs/.  
Скрипт запускается один раз и слушает ответ от сайта https://dvmn.org/api/docs/ в режиме `long-polling`.  
Если приходит ответ от сервера - сообщение отправляется в указанный телеграм чат. 

## Локальные переменные

Создайте файл `.env` и поместите в него следующие переменные.  
- DEVMAN_TOKEN_API=<[DEVMAN_TOKEN_API](https://dvmn.org/api/docs/)>
- DEBUG_MODE=`True` - если вы хотите видеть полное логирование. `False` - в лог выводится только пользовательская информация
- TELEGRAM_API_KEY=`<TELEGRAM_API_KEY>`  
В мессенджере телеграм вызовите бота [BotFather](https://t.me/BotFather/), выполните инструкции и получите `TELEGRAM_API_KEY`.
- TELEGRAM_CHAT_ID=[TELEGRAM_CHAT_ID](https://t.me/username_to_id_bot)

## Запуск

- На компьютере должен быть установлен [Python 3.10+](https://www.python.org).
- Установите виртуальное [окружение](https://docs.python.org/3/tutorial/venv.html).
- Установите зависимости командой:
``` bash
pip install -r requirements.txt
```
- Запустите команду:
```bash
python check_request.py
```

## Запуск в Docker
- Необходимо установить последнюю версию [Docker](https://www.docker.com)
- Запустите Docker container в директории, где находится файл [docker-compose](docker-compose.yml):
```bash 
docker-compose up -d
```
