import csv

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient, Tag

CSV_PATH_INGREDIENTS = 'core/data/ingredients.csv'
CSV_PATH_TAGS = 'core/data/tags.csv'


class Command(BaseCommand):
    help = 'Загружает данные об ингредиентах из csv файла в базу данных.'

    def handle(self, *args, **kwargs):
        try:
            self.load_ingredients()
            self.load_tags()
        except Exception as error:
            CommandError(error)
        print('Данные об ингредиентах и теги успешно загружены в базу данных!')

    def load_ingredients(self):
        with open(CSV_PATH_INGREDIENTS, newline='', encoding='utf-8') as file:
            for row in csv.reader(file, delimiter=','):
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1],
                )

    def load_tags(self):
        with open(CSV_PATH_TAGS, newline='', encoding='utf-8') as file:
            for row in csv.reader(file, delimiter=','):
                Tag.objects.get_or_create(
                    name=row[0],
                    color=row[1],
                    slug=row[2]
                )
