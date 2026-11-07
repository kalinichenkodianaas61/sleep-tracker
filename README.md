# Sleep tracker

Console sleep tracking program

Name: Sleep tracker
For whom: for me to see how much and how I sleep
Record: date, falling asleep time, wake up time, sleep quality (1-100%)
Operations: show all, find by quality/duration, delete
Reports: average duration/quality of sleep, shortest/longest sleep

# Запуск сервера

Команди запускати з теки проєкту, у двох окремих терміналах:

Спочатку API:
   py -m waitress --listen=127.0.0.1:8000 app:app
Потім тунель:
   cloudflared tunnel --url http://127.0.0.1:8000

Адреса тунелю з'являється в рамці на початку виводу cloudflared.
