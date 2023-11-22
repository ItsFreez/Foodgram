import csv

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient

CSV_PATH = 'core/data/ingredients.csv'


class Command(BaseCommand):
    help = 'Загружает данные об ингредиентах из csv файла в базу данных.'

    def handle(self, *args, **kwargs):
        try:
            with open(CSV_PATH, newline='', encoding='utf-8') as file:
                for row in csv.reader(file, delimiter=','):
                    Ingredient.objects.get_or_create(
                        name=row[0],
                        measurement_unit=row[1],
                    )
        except Exception as error:
            CommandError(error)
        print('Данные об ингредиентах успешно загружены в базу данных!')
