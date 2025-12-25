Запуск проекта:
python manage.py runserver

Прогрев кэша :
python manage.py sidebar_cache

Запуск почтового сервера
maildev --smtp 1025 --web 1080

Запуск centrifugo:
centrifugo -c centrifugo/config.json


Открыть:

Основа:
http://localhost:8000/

Почта:
http://localhost:1080/

Кэш:
redis::/localhost:6379/1

Центрифуга:
http://localhost:8035/