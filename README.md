# Проект Foodgram
### Описание
Перед Вами проект Foodgram, Продуктовый помощик. Учебный проект Яндекс.Практикум.
Проект ставит перед собой цели создания базы кулинарных рецептов, с описанием приготовления, его составом, временем приготовления.
Пользователь имеет возможность регистрации, просмотра рецепта, публикации своих, подписываться на других авторов, добавлять понравившиеся рецепты в избранное и затем скачивать сводный список продуктов, необходимых для приготовления.
Проект реализован через архитектуру SPA.

Адрес проекта в сети:
* Foodgram (http://51.250.106.229/)

Использовано:
* Python v.3.7.5 (https://docs.python.org/3.7/)
* Django v.2.2.19 (https://docs.djangoproject.com/en/2.2/)
* DRF v.3.12.4 (https://www.django-rest-framework.org/community/release-notes/#312x-series)
* Flake 8 v.5.0.4 (https://buildmedia.readthedocs.org/media/pdf/flake8/stable/flake8.pdf)


### Шаблон заполнения .env:
Путь к файлу: 
```
foodgram-project-react/infra/.env
```

Ниже представлены примеры заполнения:
* Тип БД
* Имя БД
* Логин для подключения к БД
* Пароль для подключени к БД
* Имя сервера/контейнера, где находятся БД
* Порт для подключения к БД
* Секретный ключ для Django
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY='a&a%000000hhaaaaa^##a0)aaa@0aaa=aa&aaaaa^##aaa0(aa'
```

### Разворачивание и запуск:
Клонировать репозиторий и перейти в папку инфраструктуры в командной строке:

```
git clone https://github.com/minigraph/foodgram-project-react.git
```

```
cd foodgram-project-react/infra
```

Cобрать и запустить контейнеры:

```
sudo docker-compose up -d --build
```

Выполнить миграции:

```
sudo docker-compose exec web python manage.py migrate
```

Создать суперпользователя:

```
docker-compose exec web python manage.py createsuperuser
```

Собрать статику:

```
sudo docker-compose exec web python manage.py collectstatic --no-input
```

Проект доступен по адресу:
```
http://51.250.106.229/
```

### Заполнить базу данных тестовыми данными:
Выполните команду в консоле:
```
sudo docker-compose exec web python manage.py load_data
```
Для доступа в административную панель:
```
login: admin
password: admin
```

### Документация. Примеры запросов:
##### Получение данных своего профиля
```
GET http://localhost/api/v1/users/me/
```
Результат запроса:
```json
{
  "id": 0,
  "username": "Luen",
  "email": "test@test.ru",
  "first_name": "Luen",
  "last_name": "",
  "is_subscribed": false
}
```

##### Получение списка всех пользователей
```
http://localhost/api/v1/users/
```
Результат запроса:
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@gmail.com",
      "first_name": "Админ",
      "last_name": "Админский",
      "is_subscribed": false
    },
    {
      "id": 2,
      "username": "Luen",
      "email": "test@test.ru",
      "first_name": "Luen",
      "last_name": "",
      "is_subscribed": false
    },
}
```
##### Запрос получения списка рецептов:
```
GET http://localhost/api/v1/recipes/
```
Ответ:
```
Status code: 200
```
```json
{
  "count": 123,
  "next": "http://localhost/api/v1/recipes/?page=2",
  "previous": null,
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
        "email": "admin@admin.com",
        "id": 0,
        "username": "admin",
        "first_name": "Tomas",
        "last_name": "Anderson",
        "is_subscribed": false
      },
      "ingredients": [
        {
          "id": 1,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "Завтрак холостяка",
      "image": "http://localhost/media/recipes/images/image.jpeg",
      "text": "Описание",
      "cooking_time": 1
    }   
  ]
}
```

##### Запрос добавления рецепта в избранное:
```
POST http://localhost/api/v1/recipes/{id}/favorite/
```
Ответы:
```
Status code: 200
```
```json
{
  "id": 0,
  "name": "Наименование рецепта",
  "image": "http://localhost/media/recipes/images/image.jpeg",
  "cooking_time": 1
}
```
```
Status code: 400
```
```json
{
  "errorr": [
    "Ошибка добавления в избранное."
  ]
}
```
```
Status code: 401
```
```json
{
  "detail": "Учетные данные не были предоставлены."
}
```

##### Запрос частичного обновления рецепта:
```
PATCH http://localhost/api/recipes/1/
```
Данные:
```json
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
  "name": "Наименование",
  "text": "Описание",
  "cooking_time": 1
}
```
Ответы:
```
Status code: 200
```
```json
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
    "email": "admin@admin.com",
    "id": 0,
    "username": "admin",
    "first_name": "Tomas",
    "last_name": "Anderson",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 1,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "Завтрак холостяка",
  "image": "http://localhost/media/recipes/images/image.jpeg",
  "text": "Описание",
  "cooking_time": 1
}
```
```
Status code: 400
```
```json
{
  "ingredients": [
    {},
    {
      "amount": [
        "Убедитесь, что это значение больше либо равно 1."
      ]
    },
    {}
  ]
}
```
```
Status code: 401
```
```json
{
  "detail": "Учетные данные не были предоставлены."
}
```
```
Status code: 403
```
```json
{
  "detail": "У вас недостаточно прав для выполнения данного действия."
}
```
```
Status code: 404
```
```json
{
  "detail": "Страница не найдена."
}
```

##### Запрос получения списка ингредиентов:
```
GET http://localhost/api/v1/ingredients/
```
Ответ:
```
Status code: 200
```
```json
[
  {
    "id": 0,
    "name": "Капуста",
    "measurement_unit": "кг"
  }
]
```

##### Запрос на подписку на пользователя:
```
POST http://localhost/api/v1/users/2/subscribe/
```
Ответы:
```
Status code: 200
```
```json
{
  "email": "cook@kitchen.com",
  "id": 3,
  "username": "cook",
  "first_name": "Gordon",
  "last_name": "Ramsy",
  "is_subscribed": true,
  "recipes": [
    {
      "id": 1,
      "name": "Рецепт",
      "image": "http://localhost/media/recipes/images/image.jpeg",
      "cooking_time": 1
    }
  ],
  "recipes_count": 1
}
```

Подробная инструкция после установки и запуска проекта по адресу:
[Документация ReDoc](http://51.250.106.229/api/docs/)

### Автор:
* Михаил Никитин
* * tlg: @minigraf 
* * e-mail: minigraph@yandex.ru;

