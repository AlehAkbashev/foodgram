# Проект Foodgram

```
Админка:
user: admin
pw: 1

Пользователь:
test@test.ru
parol1234

```

## Описание

Сервис Foodgram существует для того, чтобы пользователи могли создавать кулинарные рецепты, следить за любимыми авторами, добавлять понравившиеся рецепты в избранное или в список покупок. В списке покупок можно скачать список ингредиентов и его количества, необходимое для приготовления блюда.



 ## Как запустить проект на сервере

1. Клонировать проект из репозитория

```
git clone git@github.com:AlehAkbashev/foodgram-project-react.git
```

2. Установить Docker и Docker Compose на сервере.
 
 Выполните поочередно следующие команды.

```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh 
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin
```

3. Перенести файл `docker-compose.production.yml` в папку проекта на сервере, подставив свои значения в команду.

```
scp -i path_to_SSH/SSH_name docker-compose.production.yml \
    username@server_ip:/home/username/taski/docker-compose.production.yml
```

4. Создать и перенести файл `.env` в папку проекта на сервере. Заполнить файл `.env` следующими данными:
```
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=food_db
DB_HOST=foodgram_db
DB_PORT=5432
```

В поля POSTGRES_USER и POSTGRES_PASSWORD прописать свои значения.

5. Запустить создание контейнеров и объединение их в единую сеть.

```
sudo docker compose -f docker-compose.production.yml up -d
```

6. В редакторе Nano поправить конфиг nginx. Для домена сервиса Foodgram оставить один блок location. После изменения перезагрузить nginx.
```
location / {
        proxy_pass http://127.0.0.1:8000;
    }
```

7. Выполнить следующие команды на сервере.

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate

sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input

sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/

sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_csv

```

8. Создать Суперпользователя для входа в админку проекта.

9. В админке создать несколько тегов для категоризации рецептов.


## Какие доступны эндпоинты для API.

### Пользователи
```
/api/users/ - Список пользователей, регистрация пользователей

/api/users/{id}/ - Информация о пользователе

/api/users/me/ - Информация о себе

/api/users/set_password/ - Изменить пароль

/api/auth/token/login/ - Авторизоваться

/api/auth/token/logout/ - Деавторизоваться

/api/users/{id}/subscribe/ - Подписаться на автора с id

/api/users/subscriptions/ - Все подписки
```

### Теги

```
/api/tags/ - Все теги

/api/tags/{id}/ - Тег с определенным id.
```

### Рецепты

```
/api/recipes/ - Получение списка рецептов. Создание своего рецепта.

/api/recipes/{id}/ - Получение рецепта. Изменение рецепта. Удаление рецепта.

```

Полный список эндпоинтов можно посмотреть в документации по адресу `api/docs/`

## Пример запросов и ответов

**GET запрос на эндпоинт /api/recipes/**

Пример ответа

```
{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "color": "#E26C2D",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```

---

**POST запрос на эндпоинт /api/recipes/**

Пример запроса

```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

Пример ответа

```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```