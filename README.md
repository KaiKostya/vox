# vox

Принятые допущения:
1. Успешный ответ:  {"isSuccess": True, "errorMessage": None, "result": ...}
2. При ошибке сериализация json-а сервер возвращает 400 ошибку bad request
3. Неуспешный ответ: {"isSuccess": False, "errorMessage": "Некорректный запрос", "result": null}
4. Клиенты и заказы хранятся в БД Postgres в таблицах ClientCard, Order
5. Адрес сервера http://127.0.0.1:8080
6. Заголовки {"Content-Type": "application/json", "x-date-format": "ISO"}