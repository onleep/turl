# Tiny URL - create and manage short links
<span style="color:rgb(86, 203, 195)">**Сервис поднят прямо сейчас**</span> и доступен для каждого желающего по ссылке в описаннии github. Методы работы с сервисом описаны далее в документации. Для self-hosted решения достаточно **создать .env** файл на основе .env.dev и запустить **docker-compose**.


## <span style="color:rgb(123, 214, 92)">Technology:</span>
Проект поднимается запуском docker-compose, внутри которого поднимаются:
1. mysql
2. redis
3. Панели администрирования
4. turl сервис

Создается таблица в БД со следующей структурой:
```py
class Links(BaseModel):
    id = AutoField()
    turl = CharField(index=True, null=True, unique=True, default=None)
    url = CharField()
    token = CharField()
    stats = IntegerField(constraints=[SQL("DEFAULT 0")])
    onetime = IntegerField(constraints=[SQL("DEFAULT 0")])
    expired_at = DateTimeField(index=True, null=True, default=None)
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    updated_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')])
```
После чего запускается FastAPI сервис, где каждый запрос проходит валилацию pydantic. Генерация ссылок в котором происходит благодаря самописной функции [genturl](https://github.com/onleep/turl/blob/9375a5125ba58ff603f854a2a1cd392f4a56ee74/app/api/tools.py#L8), которая гарантирует уникальное создание ссылок на протяжении всей работы приложения. Turl могут существовать до 30 дней.

Удаление expired turl ссылок в mysql обеспечивается [cron-задачей](https://github.com/onleep/turl/blob/9375a5125ba58ff603f854a2a1cd392f4a56ee74/app/sheduler/crontab.py#L9), в Redis реализуется посредством использования встроенного механизма TTL Redis.

Кеширование: Исходные ссылки при запросах на редирект достаются из Redis для обеспечения быстродействия. И при необходимости учитываются в статистике переходов.

## <span style="color: #A680E2">Новый функционал:</span>
1. Пользователю не нужно проходить регистрацию для создания ссылок, авторизация существует на основе токена, который выдается при создании первой ссылки, с помощью которого он сможет создавать новые и управлять текущими ссылками.
2. Onetime link. Реализован метод единоразовых ссылок, после перехода на которые turl безвозвратно удаляется.
3. Hide redirect. Реализован метод редиректа без учета в статистике. Полезно, например, чтобы собственные переходы не учитывались в статистике.
4. 


## <span style="color: #A680E2">Methods:</span>
## <span style="color: #A680E2">POST</span> ***/links/shorten***
Создание turl (короткой ссылки) для переданного URL. При создании turl пользователю отдается token, с помощью которого далее он сможет управлять ссылкой.
### **Params:**  ✅ = обязательный
| `url` (string, ✅) — Исходный URL  

| `custom_alias` (string) — Кастомное имя ссылки

| `token` (string) — Токен в формате hexadecimal string  

| `expired_at` (string) — Дата истечения (YYYY-MM-DD HH:MM)  

| `onetime` (boolean) — Удалять после первого использования
```http
POST http://t.tar.nz/links/shorten
Content-Type: application/json

{
  "url": "http://google.com",
  "expired_at": "2025-03-31 18:58",
  "custom_alias": "hellow",
  "onetime": true
}
```
Пример ответа:
```json
{
  "data": {
    "turl": "http://t.tar.nz/bACHB",
    "token": "0db0a79bafb9f500797ef01be97566ec",
    "expired_at": "2025-03-31 18:58:00"
  },
  "info": {
    "custom_alias": "Turl hellow already exist"
  }
}
```

### [All request example](https://github.com/onleep/turl/blob/9375a5125ba58ff603f854a2a1cd392f4a56ee74/rest.http#L1)
P.S. Используйте rest-client для работы с файлом rest.http

## <span style="color: #A680E2">GET</span> ***/{turl}***
Редирект с короткой на изначальную ссылку
```http
GET http://t.tar.nz/{turl}
```
## <span style="color: #A680E2">DELETE</span> ***/links/shorten/***
Удаление короткой ссылки
```http
DELETE http://t.tar.nz/links/shorten
Content-Type: application/json

{
  "turl": "http://t.tar.nz/BwWFd",
  "token": "fa1309ba55fbbdaa762e1091a56f057a"
}
```
## <span style="color: #A680E2">PUT</span> ***/links/shorten***
Изменение короткой ссылки
```http
PUT http://t.tar.nz/links/shorten
Content-Type: application/json

{
  "turl": "http://t.tar.nz/BwWFd",
  "token": "fa1309ba55fbbdaa762e1091a56f057a"
}
```
## <span style="color: #A680E2">GET</span> ***/{turl}/stats***
Получение статистики ссылки
```http
GET http://t.tar.nz/hellow/stats
```
Пример ответа:
```json
{
  "data": {
    "stats": 3,
    "url": "https://google.com",
    "expired_at": "2025-03-31 18:58:00",
    "created_at": "2025-03-24 20:37:46",
    "updated_at": "2025-03-24 20:37:59"
  }
}
```
## <span style="color: #A680E2">GET</span> ***/links/search?url={url}***
Получение turl по длинной ссылке.
```http
GET http://t.tar.nz/links/search?url=https://google.com
```
