# vox

Принятые допущения:
1. Успешный ответ:  status_code: 200, body: {"isSuccess": True, "errorMessage": None, "result": {...}}
2. При ошибке сериализации json-а сервер возвращает 400 ответ, bad request
3. При несуществующем ресурсе (client_id или items) возвращается ответ 404 not found
4. Неуспешный ответ: status_code: 200, body: {"isSuccess": False, "errorMessage": "Некорректный запрос", "result": null}
5. Клиенты и заказы хранятся в БД Postgres в таблицах ClientCard, Order
6. Адрес сервера http://127.0.0.1:8080
7. Заголовки {"Content-Type": "application/json", "x-date-format": "ISO"}
