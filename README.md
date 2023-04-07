# api_yamdb

api_yamdb - итоговый командный проект учебного блока API django rest_framework. 
##  Основные фукнции
- AUTH
- TITLES
- CATEGORIES
- GENRES
- REVIEWS
- СOMMENTS
- USERS

## Установка
Download and create envirement.
```bash
git clone git@github.com:donartemiy/api_yamdb.git
cd api_yamdb
python -m venv venv
source venv/Scripts/activate
pip install -r requirements
```

## Запуск проекта

```bash
cd api_yamdb
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Примеры использования
### Произведения
Request:
```bash
curl http://127.0.0.1:8000/api/v1/titles/
```
Response:
```json
{
    "id": 1,
    "name": "Вино из одуванчиков",
    "description": "Скучная книга",
    "category": {
        "name": "Книги",
        "slug": "books"
    },
    "genre": [
        {
            "name": "Реализм",
            "slug": "realism"
        }
    ],
    "year": 1957,
    "rating": 6.0
}
```

### Другие enpoints
Requests:
```bash
curl http://127.0.0.1:8000/api/v1/category/
curl http://127.0.0.1:8000/api/v1/titles/{id}/reviews/
curl http://127.0.0.1:8000/api/v1/users/
```

### Получение Токена
Request:
```bash
curl X POST http://127.0.0.1:8000/api/v1/jwt/create/
   -H "Accept: application/json"
   -H "Authorization: Bearer <ACCESS_TOKEN>"
   -d '{"username": "string", "password": "string"}'
```
Resonse:
```json
{
  "username": "string",
  "password": "string"
}
```
   
   
### Добавление произведения
Request:
```bash
curl X POST http://127.0.0.1:8000/api/v1/titles/
   -H "Accept: application/json"
   -H "Authorization: Bearer <ACCESS_TOKEN>"
   -d '{"name": string"", "year": 0, "description": "string", "genre": ["string"], "category": "string"'}
```
Resonse:
```json
{
    "id": 0,
    "name": "string",
    "year": 0,
    "rating": 0,
    "description": "string",
    "genre": [
        {}
    ],
    "category": {
        "name": "string",
        "slug": "string"
    }
}
```

После запуска проекта доступна документация [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

# Наполнение Базы данных.
Скрипт наполнения БД расположен api_yamdb/static/data
```bash
# Переместить БД в каталог api_yamdb/static/data
mv api_yamdb/db.sqlite3 api_yamdb/static/data/db.sqlite3
# Запустить скрипт
python api_yamdb/static/data/populate_database.py
# Вернуть таблицу назад
mv api_yamdb/static/data/db.sqlite3 api_yamdb/db.sqlite3
```

# Авторы 
- alexefremov74
- temka778
- donartemiy