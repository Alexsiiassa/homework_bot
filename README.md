# homework-bot
Чат-бот Telegram для получения информации о проведенном код-ревью домашнего задания (Telegram API)

## Программа написана на Python с использованием:

requests (направление http-запроса на сервер),
python-dotenv (загрузка и считывание переменных окружения из файла .env)
python-telegram-bot (работа с Телеграм-ботом)
pySocks (направление трафика через SOCKS и HTTP прокси-серверы)
Как работает программа:
Чат-бот Телеграм обращается к API, которое возвращает изменение статуса домашнего задания и сообщает проверено ли задание, провалено или принято.

## Как запустить программу:
Клонируйте репозитроий с программой:
git clone https://github.com/Alexsiiassa/homework_bot
В созданной директории установите виртуальное окружение, активируйте его и установите необходимые зависимости:
python3 -m venv venv

. venv/bin/activate

pip install -r requirements.txt
Создайте чат-бота Телеграм
Создайте в директории файл .env и поместите туда необходимые токены в формате PRAKTIKUM_TOKEN = 'ххххххххх', TELEGRAM_TOKEN = 'ххххххххххх', TELEGRAM_CHAT_ID = 'ххххххххххх'
Откройте файл homework.py и запустите код
Пример ответа чат-бота:
{ "homeworks":[ { "id":123, "status":"approved", "homework_name":"username__hw_python_oop.zip", "reviewer_comment":"Всё нравится", "date_updated":"2020-02-13T14:40:57Z", "lesson_name":"Итоговый проект" } ], "current_date":1581604970 }
