# Проект FoodGram

## Описание проекта

«Фудграм» — проект, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Стэк технологий

- Python - 3.9.10

- Django - 3.2.3

- DjangoRestFramework - 3.12.4 

- Djoser - 2.1.0

- Docker

- Gunicorn - 20.1

- Nginx - 1.19.3

- PostgreSQL - 13.0

## Установка проекта:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com:ItsFreez/foodgram-project-react.git
```

```
cd foodgram-project-react/infra
```

Создаем файл .env с переменными окружения и заполняем его своими данными по шаблону:

```
touch .env
```

```
POSTGRES_DB="foodgram_example"
POSTGRES_USER="foodgram_user_example"
POSTGRES_PASSWORD="foodgram_password_example"
DB_NAME="foodgram_example"
DB_HOST="db_example"
DB_PORT=5432
SECRET_KEY="secret_key_example"
DEBUG="False"
ALLOWED_HOSTS="127.0.0.1,localhost"
```

Запустите docker compose:

*Windows*
```
docker compose up -d
```

*Linux*
```
sudo docker compose up -d
```

Выполните миграции в контейнере:

```
docker compose exec backend python manage.py migrate
```

Загрузите данные ингредиентов и теги (по желанию):

```
docker compose exec backend python manage.py import_csv_data
```

Скопируйте статику бэкенда:

```
docker compose exec backend python manage.py collectstatic
```

После запуска проект станет доступен по адресу - http://localhost

Документация будет доступна по адресу - http://localhost/api/docs/

### Автор проекта

[ItsFreez](https://github.com/ItsFreez)

### Активный сайт проекта

Доменное имя - https://foodgrampracticum.hopto.org

### Данные админа для проверки

Почта - Freez@yandex.ru

Пароль - foodgramproject123456
