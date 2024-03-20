# Foodgram

## Описание

**«Фудграм»** — проект, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Стэк технологий

![](https://img.shields.io/badge/Python-3.9-black?style=flat&logo=python) 
![](https://img.shields.io/badge/Django-3.2.3-black?style=flat&logo=django)
![](https://img.shields.io/badge/DjangoRestFramework-3.12.4-black?style=flat&)
![](https://img.shields.io/badge/Djoser-2.1.0-black?style=flat&logo=djoser) 
![](https://img.shields.io/badge/Docker-black?style=flat&logo=docker)
![](https://img.shields.io/badge/Gunicorn-20.1-black?style=flat&logo=gunicorn)
![](https://img.shields.io/badge/Nginx-1.19.3-black?style=flat&logo=nginx)
![](https://img.shields.io/badge/PostgreSQL-13.0-black?style=flat&logo=postgresql)

## Порядок действий для запуска проекта

***1. Клонировать репозиторий и перейти в папку c проектом***

```shell
git clone git@github.com:ItsFreez/Foodgram.git
```

```shell
cd Foodgram/infra
```

***2. Создать файл .env с переменными окружения и заполнить его данными по шаблону***

```shell
touch .env
```

```shell
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

***3. Запустить docker compose***

*Для Windows*
```shell
docker compose up -d
```

*Для MacOS/Linux*
```shell
sudo docker compose up -d
```

***4. Выполнить миграции в контейнере***

```shell
docker compose exec backend python manage.py migrate
```

***5. Заполнить базу данных проекта ингредиентами и тегами (по желанию)***

```shell
docker compose exec backend python manage.py import_csv_data
```

***6. Скопировать статику бэкенда***

```shell
docker compose exec backend python manage.py collectstatic
```

***6. Изучить эндпоинты и примеры их использования для работы с API в документации Redoc***

```shell
http://localhost/api/docs/
```

### Автор проекта

[ItsFreez](https://github.com/ItsFreez)
